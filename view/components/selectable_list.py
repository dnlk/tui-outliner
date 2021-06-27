
from typing import *

from control.selectable_list import SelectableListController
from model.selectable_list import SelectableListModel
from nodes.node_types import NodeId
from view_data_provider.selectable_list_data_provider import SelectableListDataProvider

from ..binding import Binding
from .lines import Lines


class SelectableListComponent(Lines):
    text: Binding[str]
    assigned_y: int
    assigned_height: int

    def __init__(self, width: int, model_data_provider, mode, ui_state, action_notifier, change_notifier):
        model = SelectableListModel[NodeId]()
        data_provider = SelectableListDataProvider(model, model_data_provider, mode, ui_state)

        super().__init__(data_provider, width)

        self.selected_item = Binding(self, model.get_selected_item)
        self.selectable_list_controller = SelectableListController(
            model,
            mode,
            ui_state,
            self.selected_item,
            action_notifier,
            change_notifier)
