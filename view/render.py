
from typing import *

from ext.geometry import Coord

from screen.interface import WindowInterface

from .color import Color
from .layout import Layout
from .text import Line, TextSnippet


class RenderLines:

    def __init__(self, screen: WindowInterface):
        self.screen = screen

    def _render_text_snippet(self, x: int, y: int, text: TextSnippet) -> int:
        coord = Coord(x=x, y=y)
        self.screen.print(
            text.text, coord, fg_color=text.fg_color, bg_color=text.bg_color
        )
        return x + len(text.text)

    def draw_blank_line(self, y: int, color: Color):
        coord = Coord(x=0, y=y)
        self.screen.print(
            ' ' * self.screen.width, coord, fg_color=Color.White, bg_color=color
        )

    def _render_line(self, y: int, line: Line):
        self.draw_blank_line(y, Color.Black)
        x = line.x
        for snippet in line.text_snippets:
            x = self._render_text_snippet(x, y, text=snippet)

    def render_lines(self, y_offset: int, lines: List[Line]) -> int:
        num_lines = 0
        for y, line in enumerate(lines, y_offset):
            self._render_line(y, line)
            num_lines += 1
        return num_lines


class RenderLayout:
    def __init__(self, screen: WindowInterface, layout: Layout):
        self.screen = screen
        self.layout = layout
        self.renderer = RenderLines(self.screen)

    def render_layout(self):
        self.layout.process_layout()
        for c in self.layout.components:
            lines = c.get_rendered_lines()
            num_lines = self.renderer.render_lines(c.assigned_y, lines)

            for y in range(c.assigned_y + num_lines, c.assigned_height + c.assigned_height):
                self.renderer.draw_blank_line(y, Color.Black)

        self.screen.refresh()
