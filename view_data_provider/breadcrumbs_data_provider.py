
from typing import *

from view.color import Color
from view.text import Line, simple_line
from ui import UIState


def _clamp_breadcrumb_part_text(s):
    if len(s) > 15:
        return s[:15] + '...'
    else:
        return s


class BreadcrumbsDataProvider:
    width: int

    def __init__(self, ui_state: UIState):
        self.ui_state = ui_state

    def set_width(self, width: int):
        self.width = width

    def _get_breadcrumbs_text(self) -> Line:
        breadcrumb_nodes = self.ui_state.node_path.get_breadcrumb_path()
        breadcrumb_text = ' > '.join(
            _clamp_breadcrumb_part_text(self.ui_state.node_tree.get_node(bc_id).text)
            for bc_id in breadcrumb_nodes)

        if len(breadcrumb_text) > self.width:
            num_chars_display = self.width - 3  # 3 for the '...' elipsis
            breadcrumb_text = '...' + breadcrumb_text[-num_chars_display:]

        return simple_line(breadcrumb_text, 0, bg_color=Color.Black, fg_color=Color.White)

    def _get_divider_text(self) -> Line:
        divider_text = '-' * self.width
        return simple_line(divider_text, 0, bg_color=Color.Black, fg_color=Color.White)

    def get_lines(self) -> List[Line]:
        if not self.ui_state.node_path.breadcrumbs:
            return []

        return [
            self._get_breadcrumbs_text(),
            self._get_divider_text()
        ]

    def num_lines(self) -> int:
        return 2 if self.ui_state.node_path.breadcrumbs else 0
