
from typing import *

from asciimatics.screen import Screen


from .color import Color
from .layout import Layout
from .text import Line, TextSnippet


mapped_colors = {
    Color.White: Screen.COLOUR_WHITE,
    Color.Black: Screen.COLOUR_BLACK,
    Color.Cyan: Screen.COLOUR_CYAN,
}


class RenderLines:

    def __init__(self, screen: Screen):
        self.screen = screen

    def _render_text_snippet(self, x: int, y: int, text: TextSnippet) -> int:
        bg_color = mapped_colors[text.bg_color]
        fg_color = mapped_colors[text.fg_color]
        self.screen.print_at(
            text.text, x, y, colour=fg_color, bg=bg_color
        )
        return x + len(text.text)

    def draw_blank_line(self, y: int, color: Color):
        self.screen.print_at(
            ' ' * self.screen.width, 0, y, colour=7, bg=mapped_colors[color]
        )

    def _render_line(self, y: int, line: Line):
        self.draw_blank_line(y, Color.Black)
        x = line.x
        for snippet in line.text_snippets:
            x = self._render_text_snippet(x=x, y=y, text=snippet)

    def render_lines(self, y_offset: int, lines: List[Line]) -> int:
        num_lines = 0
        for y, line in enumerate(lines, y_offset):
            self._render_line(y, line)
            num_lines += 1
        return num_lines


class RenderLayout:
    def __init__(self, screen: Screen, layout: Layout):
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
