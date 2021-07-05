"""
It's a bit unfortunate, but the MacOS (and unix in general) terminals generally do not send flexible enough data through
stdin to be able to reliably detect keyboard modifiers.

There are a few ways to do it better.
1. Run a separate process which sniffs out all events to the terminal window. This requires some elevated permissions
   though, which you may not want to give to your terminal.
2. Use a terminal emulator which passes more data through. A couple examples are xterm and kitty (which unfortunately
   are different from each other). I experimented enough to know it would work, but it's a bit of work to do this and
   of questionable benefit atm.

Some resources which could be helpful:
- Spec for terminal control codes: https://www.ecma-international.org/wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf
- Docs for kitty extended keyboard handling: https://sw.kovidgoyal.net/kitty/keyboard-protocol.html
"""


from typing import *

import curses

from .keys import Key, KeyEvent, Modifier


def _build_key_code_mappings():
    num_and_letter_codes = list(range(0x30, 0x30 + 10)) + list(range(0x41, 0x41 + 26))
    num_and_letter_enums = [Key(chr(n).lower()) for n in num_and_letter_codes]

    enum_to_code = dict(zip(num_and_letter_enums, num_and_letter_codes))
    enum_to_code.update({
        Key.LEFT: curses.KEY_LEFT,
        Key.UP: curses.KEY_UP,
        Key.RIGHT: curses.KEY_RIGHT,
        Key.DOWN: curses.KEY_DOWN,
        Key.ESCAPE: 0x1b,
        Key.BACK: curses.KEY_BACKSPACE,
        Key.DELETE: curses.KEY_DC,
        Key.SPACE: 32,
        Key.TAB: 9,
        Key.RETURN: 10,
        Key.COMMA: 44,
        Key.PERIOD: 45,
    })

    code_to_enum = {v: k for k, v in enum_to_code.items()}

    return enum_to_code, code_to_enum


_, code_to_enum = _build_key_code_mappings()


class MacOSKeyEventReader:

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def get_next_key(self) -> Optional[KeyEvent]:
        code = self.stdscr.getch()
        if code == -1:
            return

        # If it's the first of a utf8-8 sequence, then put it back and get the whole unicode character
        if 0b11000000 <= code < 0b11111000:
            self.stdscr.ungetch(code)
            u_chr = self.stdscr.get_wch()
            # Throw it away for now :(
            return

        if key := code_to_enum.get(code):
            return KeyEvent(key, set(), key.value)

        # Handle lower ascii range
        if 32 <= code <= 127:
            c = chr(code)

            try:
                key = Key(c.lower())
            except ValueError:
                # Throw away if we didn't explicitly handle it in the enum. :(
                return

            modifiers = set()
            if c.isupper():
                modifiers.add(Modifier.Shift)

            return KeyEvent(key, modifiers, key.value)




