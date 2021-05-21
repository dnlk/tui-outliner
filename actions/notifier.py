
from typing import *

from actions import actions as act
from actions.actions import Action
from changes import change as ch
import enums


class ChangeAction:
    def __init__(self, changes: List[ch.Change], action: Optional[act.Action]):
        self.changes = changes
        self.action = action


class ActionObserver(Protocol):
    mode: enums.Mode

    def determine_changes_from_action(self, action: Action) -> ChangeAction:
        ...


class ActionNotifier:

    def __init__(self):
        self._handlers: Dict[Tuple[enums.Mode, Type[Action]], ActionObserver] = {}

    def register(self, observer: ActionObserver, action_type: Type[Action]):
        key = (observer.mode, action_type)
        assert key not in self._handlers
        self._handlers[key] = observer

    def notify_action(self, action: Action) -> ChangeAction:
        key = (action.mode_origin, type(action))
        if key not in self._handlers:
            key = (enums.Mode.All, type(action))
        assert key in self._handlers
        return self._handlers[key].determine_changes_from_action(action)
