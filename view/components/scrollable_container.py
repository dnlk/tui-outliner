
from typing import *

from globals import change_notifier

from changes.change import Change, ScrollAdjust
from ext import maths
from view.layout import Height
from view.text import Line


class LineProvider(Protocol):
    def set_width(self, width: int):
        ...

    def get_lines(self, row_begin: int, num_rows: int) -> List[Line]:
        ...

    def num_lines(self) -> int:
        ...

    def refresh(self):
        ...


class ScrollableLines:
    height: Union[Height, int]
    width: int
    scroll_y: int
    line_provider: LineProvider
    scroll_pos: int

    assigned_y: int
    assigned_height: int

    def __init__(self, line_provider: LineProvider, width, height):
        self.line_provider = line_provider
        self.width = width
        self.height = height
        self.scroll_y = 0

        self.line_provider.set_width(width)

        change_notifier.register(self, ScrollAdjust)

    def get_height(self):
        return self.height

    def get_rendered_lines(self) -> List[Line]:
        self.line_provider.refresh()
        return self.line_provider.get_lines(self.scroll_y, self.assigned_height)

    def scroll_adjust(self, adjust: int):
        vertical_space = self.assigned_height
        min_scroll_pos = 0
        max_scroll_pos = max(self.line_provider.num_lines() - vertical_space, 0)
        new_scroll_y = self.scroll_y + adjust
        self.scroll_y = maths.clamp(min_scroll_pos, max_scroll_pos, new_scroll_y)

    def handle_change(self, change: Change):
        if isinstance(change, ScrollAdjust):
            self.scroll_adjust(change.scroll_diff)
        else:
            assert False, f'unhandled change: {change}'
