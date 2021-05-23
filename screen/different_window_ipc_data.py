
from dataclasses import dataclass

from ext.geometry import Coord

from events.keys import KeyEvent
from view.color import Color

PIPE_NAME = r'\\.\pipe\tui_app'
MAX_BUFFER_SIZE = 2**16


class Message:
    ...


@dataclass
class Print(Message):
    text: str
    coord: Coord
    fg_color: Color
    bg_color: Color
    attr: int
    transparent: bool


class Refresh(Message):
    ...


class Clear(Message):
    ...


@dataclass
class ScreenInfo(Message):
    width: int
    height: int


@dataclass
class Log(Message):
    text: str


@dataclass
class KeyEvent(Message):
    key: KeyEvent
