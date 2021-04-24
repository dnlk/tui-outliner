
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


#

# class NodeTreeChange:
#     node_tree: NodeTree
#
#     def __init__(self, node_tree: NodeTree):
#         self.node_tree = node_tree
#
#     def _stitch_nodes(self, node_id_1: Optional[NodeId], node_id_2: Optional[NodeId], transaction: NodeTransaction):
#         assert node_id_1 or node_id_2
#
#         if node_id_1:
#             node_1_change = transaction.append_change_node(node_id_1)
#             node_1_change.set_next_sibling_id(node_id_2)
#
#         if node_id_2:
#             node_2_change = transaction.append_change_node(node_id_2)
#             node_2_change.set_previous_sibling_id(node_id_1)
#
#     def _pop_node_from_tree(self, node_id: NodeId, transaction: NodeTransaction):
#         node = self.node_tree[node_id]
#         self._stitch_nodes(node.previous_sibling_id, node.next_sibling_id, transaction)
#
#         node_change = transaction.append_change_node(node_id)
#         node_change.set_previous_sibling_id(None)
#         node_change.set_next_sibling_id(None)
#         node_change.set_parent_id(None)
#
#     def _insert_node_after(self, node_id: NodeId, previous_sibling_id: NodeId, transaction: NodeTransaction):
#         next_sibling = self.node_tree.get_next_sibling(previous_sibling_id)
#         new_parent = self.node_tree.get_parent(previous_sibling_id)
#
#         next_sibling_id = None if next_sibling is None else next_sibling.id
#
#         node_change = transaction.append_change_node(node_id)
#         node_change.set_parent_id(new_parent.id)
#
#         self._stitch_nodes(previous_sibling_id, node_id, transaction)
#         self._stitch_nodes()
#
#         node_change.set_previous_sibling_id(previous_sibling_id)
#         node_change.set_parent_id(new_parent.id)
#         if next_sibling:
#             node_change.set_next_sibling_id(next_sibling.id)
#
#         node_change_previous_sibling = transaction.append_change_node(previous_sibling_id)
#         node_change_previous_sibling.set_next_sibling_id(node_id)
#
#         if next_sibling:
#             node_change_next_sibling = transaction.append_change_node(next_sibling.id)
#             node_change_next_sibling.set_previous_sibling_id(node_id)
#
#
#     def move_node_after(
#             self,
#             node_id: NodeId,
#             previous_sibling_id: NodeId,
#             transaction: NodeTransaction
#     ):
#         next_sibling = self.node_tree.get_next_sibling(previous_sibling_id)
#         new_parent = self.node_tree.get_parent(previous_sibling_id)
#
#         node_change = transaction.append_change_node(node_id)
#         node_change.set_previous_sibling_id(previous_sibling_id)
#         node_change.set_parent_id(new_parent.id)
#         if next_sibling:
#             node_change.set_next_sibling_id(next_sibling.id)
#
#         node_change_previous_sibling = transaction.append_change_node(previous_sibling_id)
#         node_change_previous_sibling.set_next_sibling_id(node_id)
#
#         if next_sibling:
#             node_change_next_sibling = transaction.append_change_node(next_sibling.id)
#             node_change_next_sibling.set_previous_sibling_id(node_id)
#
#     def insert_node_after(
#             self,
#             previous_sibling_id,
#             transaction: NodeTransaction
#     ) -> NodeId:
#         previous_sibling = self.node_tree[previous_sibling_id]
#         parent_id = previous_sibling.parent_id
#         next_sibling = self.node_tree.get_next_sibling(previous_sibling_id)
#
#         new_node = transaction.append_new_node(parent_id)
#         new_node.previous_sibling_id = previous_sibling_id
#         if next_sibling:
#             new_node.next_sibling_id = next_sibling.id
#
#         previous_sibling_change = transaction.append_change_node(previous_sibling_id)
#         previous_sibling_change.set_next_sibling_id(new_node.id)
#
#         if next_sibling:
#             next_sibling_change = transaction.append_change_node(next_sibling.id)
#             next_sibling_change.set_previous_sibling_id(new_node.id)
#
#         return new_node.id
#
#     def reparent_node_to_end_of_parent(
#             self,
#             node_id,
#             new_parent_id,
#             transaction: NodeTransaction
#     ):
#         node = self.node_tree[node_id]
#         parent = self.node_tree[new_parent_id]
#         last_child = self.node_tree.get_last_child(parent.id)
#         initial_previous_sibling = node.previous_sibling_id
#         initial_next_sibling = node.next_sibling_id
#
#         self._stitch_nodes(initial_previous_sibling, initial_next_sibling)
#
#         node_change = transaction.append_change_node(node_id)
#         node_change.set_parent_id(new_parent_id)
#         previous_sibling_id = None if last_child is None else last_child.id
#         node_change.set_previous_sibling_id(previous_sibling_id)
#
#         if last_child:
#             last_child_change = transaction.append_change_node(last_child.id)
#             last_child_change.set_previous_sibling_id(node_id)
#
#     def expand_node(
#             self,
#             node_id: NodeId,
#             transaction: NodeTransaction
#     ):
#         changes = transaction.append_change_node(node_id)
#         changes.set_expanded(True)
