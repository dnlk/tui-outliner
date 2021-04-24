
from typing import *

import consts
from node import NodeData
from node_types import NodeId
import tree


class NodeContext(tree.NodeContext[NodeId, NodeData]):
    pass


class NodeTree(tree.NodeTree[NodeId, NodeData]):
    root_node: NodeId

    def __init__(self, *args, **kwargs):
        self.root_node = NodeId(consts.ROOT_NODE_ID)
        super().__init__(*args, **kwargs)
        self.nodes[self.root_node] = NodeData(
            type=0,
            text=consts.ROOT_NODE_TEXT,
            expanded=True
        )

    def get_node(self, _id: NodeId):
        return super().get_node(_id)

    def set_root_node(self, _id: NodeId):
        self.root_node = _id

    @property
    def first_node(self) -> NodeId:
        return self.tree.get_first_child(self.root_node)

    def is_root(self, _id: NodeId) -> bool:
        return _id.id == self.root_node.id

    def is_only_descendant_of_root(self, _id: NodeId) -> bool:
        ancestors = self.tree.get_ancestors(_id)
        assert self.root_node in ancestors, 'Assume that this node is a descendant'
        # The first index is always `_id`, so check the second index
        return ancestors[1] == self.root_node and len(self.tree.get_children(self.root_node)) == 1

    def is_ancestor_of_root(self, _id: NodeId) -> bool:
        return self.tree.is_ancestor(_id, self.root_node)

    def get_depth(self, _id: NodeId) -> int:
        return self.tree.get_depth_relative_to(_id, self.root_node)

    def set_expanded(self, _id: NodeId, expanded: bool):
        self.get_node(_id).expanded = expanded

    def is_expanded(self, _id: NodeId) -> bool:
        return self.get_node(_id).expanded
