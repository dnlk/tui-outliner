
from dataclasses import dataclass

from enum import Enum
from typing import Optional


class IdType(Enum):
    DB = 0
    Temp = 1


class NodeId:
    id: Optional[int]

    def __init__(self, node_id: Optional[int], node_type: IdType = IdType.DB):
        self.id = node_id
        self.type = node_type

    def is_none(self) -> bool:
        return self.id is None

    def __bool__(self) -> bool:
        return not self.is_none()

    def __hash__(self):
        assert self.id is not None
        return hash((self.id, self.type.value))

    def __eq__(self, other):
        return other is not None and (self.id, self.type) == (other.id, other.type)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<{id}, {type}>'.format(id=self.id, type=self.type)


class PreviousNodeType(Enum):
    Parent = 0
    Sibling = 1


@dataclass
class PreviousNode:
    previous_node_id: NodeId
    previous_node_type: PreviousNodeType

    def __hash__(self):
        return hash((self.previous_node_id, self.previous_node_type))


class PreviousNodeParent(PreviousNode):
    def __init__(self, parent_id: NodeId):
        super().__init__(parent_id, PreviousNodeType.Parent)


class PreviousNodeSibling(PreviousNode):
    def __init__(self, sibling_id: NodeId):
        super().__init__(sibling_id, PreviousNodeType.Sibling)
