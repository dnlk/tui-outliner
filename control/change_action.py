
from common_imports import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from ui.edit import Edit
from enums import Mode
from ui.ui import UIState


class ActionToChange:

    node_edit: Edit
    mode = Mode.All

    def __init__(self, action_notifier: ActionNotifier, ui_state: UIState):
        self.node_tree = ui_state.node_tree
        self.selection = ui_state.selection
        self.node_edit = ui_state.node_edit
        self.screen = ui_state.screen
        self.ui_state = ui_state

        action_notifier.register(self, act.ChangeMode)
        action_notifier.register(self, act.NoOp)

    def determine_changes_from_action(self, action: act.Action) -> ChangeAction:
        changes: List[ch.Change] = []
        if action.is_type(act.ChangeMode):
            changes.append(ch.ChangeMode(action.mode))
        elif action.is_type(act.NoOp):
            ...
        else:
            logging.info(f'Unhandled action: {action}')

        return ChangeAction(changes, action)
