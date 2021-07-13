
from common_imports import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from enums import Mode
from model.selectable_list import SelectableListModel
from ui.ui import UIState
from view.binding import Binding


class SelectableListController:

    def __init__(
            self,
            model: SelectableListModel,
            mode: Mode,
            ui_state: UIState,
            selected_item_binding: Binding,
            action_notifier: ActionNotifier,
            change_notifier: ch.ChangeNotifier):
        self.model = model
        self.mode = mode
        self.ui_state = ui_state
        self.selected_item_binding = selected_item_binding
        self.node_edit = ui_state.node_edit

        action_notifier.register(self, act.NavigateDown)
        action_notifier.register(self, act.NavigateUp)

        change_notifier.register(self, ch.SelectItem)

    def determine_changes_from_action(self, action: act.Action) -> ChangeAction:
        changes: List[ch.Change] = []
        if isinstance(action, act.NavigateDown):
            if (next_item := self.model.get_next_item()) is None:
                next_item = self.model.get_first_item()
            changes.append(ch.SelectItem(next_item.id).with_mode(self.mode))
        elif isinstance(action, act.NavigateUp):
            if (next_item := self.model.get_previous_item()) is None:
                next_item = self.model.get_first_item()
            changes.append(ch.SelectItem(next_item.id).with_mode(self.mode))
        return ChangeAction(changes, action)

    def handle_change(self, change: ch.Change):
        if isinstance(change, ch.SelectItem):
            self.model.selected_item = change.item_id
            self.selected_item_binding.notify()
        else:
            assert f'Change not handled: {change}'
