
from asciimatics.screen import ManagedScreen, Screen

from ext.geometry import Coord

from events.windows_keyboard_events import WindowsKeyEventReader
from view.color import Color


class SameWindowScreen:
    _ASCIIMATICS_MAPPED_COLORS = {
        Color.White: Screen.COLOUR_WHITE,
        Color.Black: Screen.COLOUR_BLACK,
        Color.Cyan: Screen.COLOUR_CYAN,
    }

    def __init__(self):
        self._managed_screen = ManagedScreen()

    def __enter__(self):
        self._managed_screen.__enter__()
        self.width = self._managed_screen.screen.width
        self.height = self._managed_screen.screen.height
        self.event_reader = WindowsKeyEventReader()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._managed_screen.__exit__(exc_type, exc_val, exc_tb)

    def get_next_key(self):
        return self.event_reader.get_next_key()

    def print(self, text, coord: Coord, fg_color: Color, bg_color: Color, attr=0, transparent=False):
        x = coord.x
        y = coord.y
        am_fg_colour = self._ASCIIMATICS_MAPPED_COLORS[fg_color]
        am_bg_colour = self._ASCIIMATICS_MAPPED_COLORS[bg_color]
        self._managed_screen.screen.print_at(text, x, y, am_fg_colour, attr, am_bg_colour, transparent)

    def refresh(self):
        self._managed_screen.screen.refresh()

    def clear(self):
        self._managed_screen.screen.clear()
