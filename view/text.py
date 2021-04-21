
from dataclasses import dataclass

from typing import *

from view.color import Color


@dataclass
class TextSnippet:
    text: str
    bg_color: Color
    fg_color: Color


@dataclass
class Line:
    text_snippets: List[TextSnippet]
    x: int


def simple_line(s: str, x_offset: int, bg_color: Color, fg_color: Color):
    return Line(
        [
            TextSnippet(text=s, bg_color=bg_color, fg_color=fg_color)
        ],
        x_offset
    )
