
from common_imports import *

import actions.actions as act
from actions.notifier import ActionNotifier, ChangeAction
import changes.change as ch
from data.data import Data
from enums import Mode


class NodeFilterController:
    mode: Mode = Mode.Filter

    def __init__(self, action_notifier: ActionNotifier, text_editor_data: Data[str]):
        self.text_editor_data = text_editor_data

        action_notifier.register(self, act.FinishEditing)
        text_editor_data.register_listener(self)

    def handle_data_change(self, data: Data[str]) -> ChangeAction:
        changes: List[ch.Change] = []
        if data is self.text_editor_data:
            changes.append(ch.UpdateNodeFilter(self.text_editor_data.value))

        return ChangeAction(changes, None)

    def determine_changes_from_action(self, action: act.Action):
        changes: List[ch.Change] = []
        if isinstance(action, act.FinishEditing):
            changes.append(ch.ChangeMode(Mode.Navigate))
        return ChangeAction(changes, action)
