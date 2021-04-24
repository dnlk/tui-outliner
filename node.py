
from dataclasses import dataclass

from typing import *

from node_types import NodeId, IdType, PreviousNodeType, PreviousNode


@dataclass
class NodeData:
    type: int = 0
    text: str = ''
    expanded: bool = True


@dataclass
class LinkedNode:
    id: NodeId
    node_data: NodeData
    previous_sibling_id: NodeId = NodeId(None)
    previous_sibling_type: PreviousNodeType = PreviousNodeType.Sibling

    @property
    def previous_sibling(self) -> PreviousNode:
        return PreviousNode(self.previous_sibling_id, self.previous_sibling_type)

    @previous_sibling.setter
    def previous_sibling(self, previous_node: PreviousNode):
        self.previous_sibling_id = previous_node.previous_node_id
        self.previous_sibling_type = previous_node.previous_node_type

    def __repr__(self):
        return '<id: {id}, ' \
               'previous_sibling_id: {previous_sibling_id}, ' \
               'previous_sibling_type: {previous_sibling_type}' \
               'next_sibling_id: {next_sibling_id}>'\
            .format(**self.__dict__)


__last_temp_id = 0


def get_next_available_temp_id():
    global __last_temp_id
    __last_temp_id += 1
    return NodeId(__last_temp_id, IdType.Temp)


class NodeManager:

    def __init__(self, node_tree, conn):
        self.node_tree = node_tree
        self.conn = conn
