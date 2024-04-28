
from dataclasses import dataclass
from enum import Enum
from common_imports import *

from datastructures.text_editor import Cursor, ParagraphId
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
        assert key in self._handlers, key
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
class ClearText(Change):
    ...


@dataclass
class RemoveCharacter(Change):
    cursor: Cursor


@dataclass
class NewParagraph(Change):
    cursor: Cursor
    new_id: ParagraphId


@dataclass
class MergeParagraphs(Change):
    p_id1: ParagraphId
    p_id2: ParagraphId


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


@dataclass
class UpdateNodeSearch(Change):
    text: str


@dataclass
class SelectItem(Change):
    item_id: Any
