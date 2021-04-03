
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union, TypeVar, Optional, Dict, Any

from enums import Mode, TreeLink
from node_types import NodeId, PreviousNode
from text_editor import Cursor


# @dataclass
# class NewNode:
#     id: NodeId
#     previous_node: PreviousNode

@dataclass
class NewNodeNextSibling:
    id: NodeId
    previous_id: NodeId


@dataclass
class MoveNode:
    id: NodeId
    previous_node_id: NodeId
    link_type: TreeLink


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
class NewSelection:
    node_id: NodeId


@dataclass
class ChangeMode:
    mode: Mode


@dataclass
class AddCharacter:
    cursor: Cursor
    char: str


@dataclass
class SetCursor:
    cursor: Cursor


@dataclass
class RemoveCharacter:
    cursor: Cursor


@dataclass
class SetNodeText:
    id: NodeId
    text: str


Change = Union[NodeChange, NewNodeNextSibling, NewSelection, MoveNode, AddCharacter, SetCursor]



