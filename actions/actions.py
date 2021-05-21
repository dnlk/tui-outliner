
from dataclasses import dataclass

from enums import Mode


class Action:
    mode_origin: Mode = Mode.All

    def is_type(self, cls):
        return isinstance(self, cls)


class NoOp(Action):
    ...


class _Navigate(Action):
    def __init__(self, num_rows: int):
        self.num_rows = num_rows


class NavigateDown(_Navigate):
    pass


class NavigateUp(_Navigate):
    pass


class NewNodeNextSibling(Action):
    pass


class TabNode(Action):
    pass


class UntabNode(Action):
    pass


@dataclass
class ChangeMode(Action):
    mode: Mode


@dataclass
class AddCharacterToEdit(Action):
    char: str


@dataclass
class SetCursor(Action):
    cursor_pos: int


@dataclass
class CursorIncrement(Action):
    pass


@dataclass
class CursorDecrement(Action):
    pass


@dataclass
class CursorRowIncrement(Action):
    pass


@dataclass
class CursorRowDecrement(Action):
    pass


@dataclass
class RemoveCharacterBeforeCursor(Action):
    pass


@dataclass
class RemoveCharacterAtCursor(Action):
    pass


@dataclass
class FinishEditing(Action):
    pass


@dataclass
class DeleteSelectedNodeAndSelectNext(Action):
    pass


@dataclass
class DeleteSelectedNodeAndSelectPrevious(Action):
    pass


@dataclass
class MoveSelectedNodeUp(Action):
    pass


@dataclass
class MoveSelectedNodeDown(Action):
    pass


@dataclass
class DiveIntoSelectedNode(Action):
    pass


@dataclass
class ClimbOutOfNode(Action):
    pass


@dataclass
class ToggleNodeExpanded(Action):
    pass


@dataclass
class ScrollDown(Action):
    pass


@dataclass
class ScrollUp(Action):
    pass
