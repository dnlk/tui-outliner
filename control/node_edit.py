
from common_imports import *

import actions.actions as act
from actions.notifier import ActionNotifier, ChangeAction
import changes.change as ch
from enums import Mode
from ui.ui import UIState


class NodeEditController:
    mode: Mode = Mode.EditNode

    def __init__(
            self, ui_state: UIState,
            action_notifier: ActionNotifier):
        self.ui_state = ui_state

        action_notifier.register(self, act.FinishEditing)

    def determine_changes_from_action(self, action: act.Action):
        changes: List[ch.Change] = []
        if isinstance(action, act.FinishEditing):
            changes.append(ch.ChangeMode(Mode.Navigate))
            changes.append(
                ch.SetNodeText(self.ui_state.selection.selected_node_id, self.ui_state.node_edit.text_editor.get_data()))

        return ChangeAction(changes, action)
