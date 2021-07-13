
from dataclasses import dataclass

from common_imports import *

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


def line_with_cursor(
        s: str,
        x_offset: int,
        cursor_pos: int,
        text_bg: Color,
        text_fg: Color,
        cursor_bg: Color,
        cursor_fg: Color
):
    s += ' '  # Hack to make extra character for cursor
    return Line(
        [
            TextSnippet(s[:cursor_pos], bg_color=text_bg, fg_color=text_fg),
            TextSnippet(s[cursor_pos: cursor_pos + 1], bg_color=cursor_bg, fg_color=cursor_fg),
            TextSnippet(s[cursor_pos + 1:], bg_color=text_bg, fg_color=text_fg),
        ],
        x=x_offset
    )
