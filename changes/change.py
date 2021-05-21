
from dataclasses import dataclass
from enum import Enum
from typing import *

from datastructures.text_editor import Cursor
from enums import Mode, TreeLink
from nodes.node_types import NodeId
from ui.node_path import NodePath


class Change:
    mode: Mode = Mode.All

    def with_mode(self, mode: Mode) -> 'Change':
        self.mode = mode
        return self

    def __hash__(self):
        return self.__class__.__name__


class ChangeHandler(Protocol):
    mode: Mode

    def handle_change(self, change: Change):
        ...


class ChangeNotifier:

    def __init__(self):
        self._handlers: Dict[Tuple[Mode, Type[Change]], ChangeHandler] = {}

    def register(self, handler: ChangeHandler, change_type: Type[Change]):
        key = (handler.mode, change_type)
        assert key not in self._handlers
        self._handlers[key] = handler

    def notify(self, change: Change):
        key = (change.mode, type(change))
        if key not in self._handlers:
            key = (Mode.All, type(change))
        assert key in self._handlers
        self._handlers[key].handle_change(change)

    def notify_changes(self, changes: List[Change]):
        for ch in changes:
            self.notify(ch)


class ChangeType(Enum):
    parent_id = "parent_id"
    previous_sibling_id = "previous_sibling_id"
    next_sibling_id = "next_sibling_id"
    type = "type"
    text = "text"
    expanded = "expanded"


class NodeChange:
    changes: Dict[ChangeType, Any]

    def __init__(self, node_id: NodeId):
        self.node_id = node_id
        self.changes = {}

    def set_parent_id(self, node_id: Optional[NodeId]):
        self.changes[ChangeType.parent_id] = node_id

    def set_previous_sibling_id(self, node_id: Optional[NodeId]):
        self.changes[ChangeType.previous_sibling_id] = node_id

    def set_next_sibling_id(self, node_id: Optional[NodeId]):
        self.changes[ChangeType.next_sibling_id] = node_id

    def set_type(self, node_type: int):
        self.changes[ChangeType.type] = node_type

    def set_text(self, text: str):
        self.changes[ChangeType.text] = text

    def set_expanded(self, expanded: bool):
        self.changes[ChangeType.expanded] = expanded

    def __repr__(self):
        return '[id: {}, '.format(self.node_id) + ', '.join([repr(k) + ': ' + repr(v) for k, v in self.changes.items()]) + ']'


@dataclass
class InsertNewNodeAfter(Change):
    node_id: NodeId
    previous_id: NodeId
    link_type: TreeLink


@dataclass
class MoveNode(Change):
    id: NodeId
    previous_node_id: NodeId
    link_type: TreeLink


@dataclass
class NewSelection(Change):
    node_id: NodeId


@dataclass
class ChangeMode(Change):
    mode: Mode


@dataclass
class AddCharacter(Change):
    cursor: Cursor
    char: str


@dataclass
class SetCursor(Change):
    cursor: Cursor


@dataclass
class RemoveCharacter(Change):
    cursor: Cursor


@dataclass
class SetNodeText(Change):
    id: NodeId
    text: str


@dataclass
class DeleteNode(Change):
    node_id: NodeId


@dataclass
class SetRootNode(Change):
    node_id: NodeId


@dataclass
class SetExpanded(Change):
    node_id: NodeId
    expanded: bool


@dataclass
class SetNodePath(Change):
    node_path: NodePath


@dataclass
class ScrollAdjust(Change):
    scroll_diff: int


@dataclass
class UpdateNodeFilter(Change):
    text: str
