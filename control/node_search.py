
from common_imports import *

import actions.actions as act
from actions.notifier import ActionNotifier, ChangeAction
import changes.change as ch
from control.common import ChangesForAction
from data.data import Data
from enums import Mode
from nodes.node_types import NodeId
from ui.ui import UIState


class NodeSearchController:
    mode: Mode = Mode.Search

    def __init__(
            self, ui_state: UIState,
            action_notifier: ActionNotifier,
            text_editor_data: Data[str],
            selected_search_item_data: Data[NodeId]):
        self.ui_state = ui_state
        self.text_editor_data = text_editor_data
        self.selected_search_item_data = selected_search_item_data

        action_notifier.register(self, act.FinishEditing)
        text_editor_data.register_listener(self)
        selected_search_item_data.register_listener(self)

    def handle_data_change(self, data: Data) -> ChangeAction:
        changes: List[ch.Change] = []
        if data is self.text_editor_data:
            changes.append(ch.UpdateNodeSearch(self.text_editor_data.value))

        return ChangeAction(changes, None)

    def determine_changes_from_action(self, action: act.Action):
        changes: List[ch.Change] = []
        if isinstance(action, act.FinishEditing):
            changes.append(ch.ClearText().with_mode(self.mode))
            changes.append(ch.ChangeMode(Mode.Navigate))
            if self.selected_search_item_data.value:
                ChangesForAction(self.ui_state).dive_into_node(changes, self.selected_search_item_data.value)

        return ChangeAction(changes, action)
