
from typing import *

from data.data import Data
from model.selectable_list import SelectableListModel
from view.color import Color
from view.text import Line, simple_line
from ui.ui import UIState


class SelectableListDataProvider:
    width: int

    def __init__(self, model: SelectableListModel, model_data_provider, mode, ui_state: UIState):
        self.mode = mode
        self.model = model
        self.model_data_provider = model_data_provider
        self.ui_state = ui_state
        self.selected_index = None

    def set_width(self, width: int):
        self.width = width

    def _selected_line(self, text: str) -> Line:
        return simple_line(
            text,
            0,
            Color.Cyan,
            Color.White,
        )

    def _unselected_line(self, text: str) -> Line:
        return simple_line(
            text,
            0,
            Color.Black,
            Color.White,
        )

    def get_lines(self) -> List[Line]:
        if self.mode != self.ui_state.mode:
            return []
        return [
            self._selected_line(item.text) if self.model.is_selected(item) else self._unselected_line(item.text)
            for item in self.model.get_items()
        ]

    def num_lines(self) -> int:
        self.model.set_items(self.model_data_provider.get_items())
        if self.mode == self.ui_state.mode:
            return self.model_data_provider.num_max_results
        else:
            return 0
