
from common_imports import *

from enums import Mode
from model.selectable_list import SelectableItem
from nodes.node_types import NodeId
from ui.ui import UIState
from view.color import Color
from view.text import Line, simple_line


class SearchResultsDataProvider:
    def __init__(self, num_max_results: int, ui_state: UIState):
        self.num_max_results = num_max_results
        self.search = ui_state.search

    def get_items(self) -> List[SelectableItem[NodeId]]:
        items = []
        for node_context in self.search.get_results():
            items.append(SelectableItem(node_context.id, node_context.node.text))
        return items
