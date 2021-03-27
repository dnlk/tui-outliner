"""
https://stackoverflow.com/questions/9750588/how-to-get-ctrl-shift-or-alt-with-getch-ncurses
https://stackoverflow.com/questions/22362076/how-to-detect-curses-alt-key-combinations-in-python
https://invisible-island.net/ncurses/ncurses.faq.html#modified_keys

"""


from win32api import STD_INPUT_HANDLE
from win32console import GetStdHandle, KEY_EVENT, ENABLE_ECHO_INPUT, ENABLE_LINE_INPUT, ENABLE_PROCESSED_INPUT
import win32console
import win32con

import asyncio


ALT = 1
CTRL = 1 << 1
SHIFT = 1 << 2

class Modifiers:
    def __init__(self, alt: bool, ctrl: bool, shift: bool):
        self.alt = alt
        self.ctrl = ctrl
        self.shift = shift


class KeyboardEvent:
    def __init__(self, base_key: int, modifiers: Modifiers, char: str):
        self.base_key = base_key
        self.modifiers = modifiers
        self.char = char

    def __eq__(self, other: 'KeyboardEvent'):
        return self.base_key == other.base_key and self.modifiers == other.modifiers


def _build_virtual_key_code_mappings():
    num_and_letter_codes = list(range(0x30, 0x30 + 10)) + list(range(0x41, 0x41 + 26))
    num_and_letter_chrs = [ord(n) for n in num_and_letter_codes]

    chr_to_code = dict(zip(num_and_letter_chrs, num_and_letter_codes))
    chr_to_code.update({
        'left_arrow': win32con.VK_LEFT,
        'up_arrow': win32con.VK_UP,
        'right_arrow': win32con.VK_RIGHT,
        'down_arrow': win32con.VK_DOWN,
    })

    code_to_chr = dict(zip(num_and_letter_codes, num_and_letter_chrs))

    return chr_to_code, code_to_chr


async def windows_keyboard_event():
    chr_to_code, code_to_chr = _build_virtual_key_code_mappings()

    stdin_handle = GetStdHandle(STD_INPUT_HANDLE)
    stdin_handle.SetConsoleMode(ENABLE_LINE_INPUT|ENABLE_ECHO_INPUT|ENABLE_PROCESSED_INPUT)

    num_events_seen = 0

    while True:
        events_peek = stdin_handle.PeekConsoleInput(10000)

        if len(events_peek) == num_events_seen:
            await asyncio.sleep(.01)
            continue

        new_events = events_peek[num_events_seen:]
        num_events_seen = len(events_peek)

        for new_event in new_events:
            if not new_event.EventType == KEY_EVENT:
                modifiers = Modifiers(
                    alt=bool(new_event.ControlKeyState & (win32con.LEFT_ALT_PRESSED | win32con.RIGHT_ALT_PRESSED)),
                    ctrl=bool(new_event.ControlKeyState & (win32con.LEFT_CTRL_PRESSED | win32con.RIGHT_CTRL_PRESSED)),
                    shift=bool(new_event.ControlKeyState & win32con.SHIFT_PRESSED),
                )
                char = new_event.Char
                char = char if not (len(char) == 1 and char[0] == '\x00') else ''
                yield KeyboardEvent(
                    base_key=code_to_chr.get(new_event.VirtualKeyCode),
                    modifiers=modifiers,
                    char=char
                )


