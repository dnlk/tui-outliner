
from typing import *

from node_tree import NodeTree
from node_types import NodeId


class Selection:
    def __init__(self, node_tree: NodeTree):
        self._selected_node_id: NodeId = None
        self.node_tree = node_tree

    @property
    def selected_node_id(self) -> NodeId:
        return self._selected_node_id

    @selected_node_id.setter
    def selected_node_id(self, node_id: NodeId):
        self._selected_node_id = node_id

    def is_selected(self, node_id) -> bool:
        return node_id == self.selected_node_id

    def get_selected_node(self) -> NodeId:
        return self.selected_node_id

    def get_next_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        node = self.node_tree.get_node(node_id)

        if node is None:
            return self._selected_node_id

        # If it's expanded then get its first child
        if node.expanded and (first_child_id := self.node_tree.tree.get_first_child(node_id)):
            return first_child_id

        # Otherwise, get the first parent with a sibling
        while node_id not in (self.node_tree.root_node, None):
            if next_node := self.node_tree.tree.get_next_sibling(node_id):
                return next_node
            node_id = self.node_tree.tree.get_parent(node_id)

        return self._selected_node_id

    def get_previous_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        if previous_sibling := self.node_tree.tree.get_previous_sibling(node_id):
            if not self.node_tree.is_root(previous_sibling):
                previous_node = previous_sibling
                while last_child := self.node_tree.tree.get_last_child(previous_node):
                    previous_node = last_child
                return previous_node
        elif (parent_node := self.node_tree.tree.get_parent(node_id)) not in (self.node_tree.root_node, None):
            return parent_node

        return node_id

    def select_next_node(self):
        if next_node := self.get_next_node():
            self.selected_node_id = next_node

    def select_previous_node(self):
        if previous_node := self.get_previous_node():
            self.selected_node_id = previous_node
