
from common_imports import *

from ext.geometry import Coord

from view.color import Color


class WindowInterface(Protocol):
    width: int
    height: int

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    def print(self, text, coord: Coord, fg_color: Color, bg_color: Color, attr=0, transparent=False):
        ...

    def refresh(self):
        ...

    def clear(self):
        ...

    def get_next_key(self):
        ...
