
from common_imports import *

from ..color import Color
from ..layout import Height
from ..text import simple_line, Line


class SimpleLine:
    assigned_y: int
    assigned_height: int

    def __init__(self, line: str, bg_color: Color, fg_color: Color):
        self.line = line
        self.bg_color = bg_color
        self.fg_color = fg_color

    def get_height(self) -> Union[int, Height]:
        return 1

    def get_rendered_lines(self) -> List[Line]:
        return [
            simple_line(self.line, 0, self.bg_color, self.fg_color)
        ]
