
from common_imports import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from enums import Mode
from ui.ui import UIState


class NodeTreeController:
    mode: Mode = Mode.EditNode

    def __init__(self, action_notifier: ActionNotifier, ui_state: UIState):
        self.ui_state = ui_state

        action_notifier.register(self, act.FinishEditing)

    def determine_changes_from_action(self, action: act.Action) -> ChangeAction:
        changes: List[ch.Change] = []
        if isinstance(action, act.FinishEditing):
            changes.append(ch.ChangeMode(Mode.Navigate))
            changes.append(ch.SetNodeText(self.ui_state.selection.selected_node_id, self.ui_state.node_edit.text_editor.get_data()))

        return ChangeAction(changes, action)
