"""
https://stackoverflow.com/questions/9750588/how-to-get-ctrl-shift-or-alt-with-getch-ncurses
https://stackoverflow.com/questions/22362076/how-to-detect-curses-alt-key-combinations-in-python
https://invisible-island.net/ncurses/ncurses.faq.html#modified_keys
"""

from common_imports import *

from win32api import STD_INPUT_HANDLE
from win32console import GetStdHandle, KEY_EVENT, ENABLE_ECHO_INPUT, ENABLE_LINE_INPUT, ENABLE_PROCESSED_INPUT
import win32con
from typing import Optional, Set

from .keys import Key, KeyEvent, Modifier


def _build_virtual_key_code_mappings():
    num_and_letter_codes = list(range(0x30, 0x30 + 10)) + list(range(0x41, 0x41 + 26))
    num_and_letter_enums = [Key(chr(n).lower()) for n in num_and_letter_codes]

    enum_to_code = dict(zip(num_and_letter_enums, num_and_letter_codes))
    enum_to_code.update({
        Key.LEFT: win32con.VK_LEFT,
        Key.UP: win32con.VK_UP,
        Key.RIGHT: win32con.VK_RIGHT,
        Key.DOWN: win32con.VK_DOWN,
        Key.ESCAPE: win32con.VK_ESCAPE,
        Key.BACK: win32con.VK_BACK,
        Key.DELETE: win32con.VK_DELETE,
        Key.SPACE: win32con.VK_SPACE,
        Key.TAB: win32con.VK_TAB,
        Key.RETURN: win32con.VK_RETURN,
    })

    code_to_enum = {v: k for k, v in enum_to_code.items()}

    return enum_to_code, code_to_enum


_, windows_code_to_key_enum = _build_virtual_key_code_mappings()


def _extract_modifiers(key_event) -> Set[Modifier]:
    modifiers = set()
    if key_event.ControlKeyState & (win32con.LEFT_ALT_PRESSED | win32con.RIGHT_ALT_PRESSED):
        modifiers.add(Modifier.Alt)
    if key_event.ControlKeyState & (win32con.LEFT_CTRL_PRESSED | win32con.RIGHT_CTRL_PRESSED):
        modifiers.add(Modifier.Control)
    if key_event.ControlKeyState & win32con.SHIFT_PRESSED:
        modifiers.add(Modifier.Shift)
    return modifiers


class WindowsKeyEventReader:
    def __init__(self):

        self.readHandle = GetStdHandle(STD_INPUT_HANDLE)
        self.readHandle.SetConsoleMode(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT|ENABLE_PROCESSED_INPUT)
        self.num_windows_key_events_handled = 0

    def _get_next_event(self):
        events_peek = self.readHandle.PeekConsoleInput(10000)
        if len(events_peek) > self.num_windows_key_events_handled:
            next_event = events_peek[self.num_windows_key_events_handled]
            self.num_windows_key_events_handled += 1
            if next_event.EventType == KEY_EVENT and next_event.KeyDown:
                return next_event

    def get_next_key(self) -> Optional[KeyEvent]:
        next_event = self._get_next_event()

        if next_event is None:
            return None

        next_event_virtual_keycode = next_event.VirtualKeyCode

        if next_event_virtual_keycode not in windows_code_to_key_enum:
            logging.info(f'Unhandled key: {next_event_virtual_keycode}')
            return None

        key = windows_code_to_key_enum[next_event_virtual_keycode]
        modifiers = _extract_modifiers(next_event)
        char = next_event.Char
        char = char if not (len(char) == 1 and char[0] == '\x00') else ''

        return KeyEvent(key, modifiers, char)


# if __name__ == '__main__':
#     import time
#     key_reader = WindowsKeyEventReader()
#     while True:
#         time.sleep(.01)
#         key_event = key_reader.get_next_key()
#         if key_event:
#             print(key_event)
