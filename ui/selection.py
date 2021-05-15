
from typing import *

from nodes.node_tree import NodeTree
from nodes.node_types import NodeId
from filter import Filter


class Selection:
    def __init__(self, node_tree: NodeTree, filter: Filter):
        self._selected_node_id: NodeId = None
        self.node_tree = node_tree
        self.filter = filter

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

    def get_next_from(self, node_id: NodeId) -> Optional[NodeId]:
        node = self.node_tree.get_node(node_id)

        if node is None:
            return None

        # If it's expanded then get its first child
        if node.expanded and (first_child_id := self.node_tree.tree.get_first_child(node_id)):
            return first_child_id

        # Otherwise, get the next sibling or first parent with a sibling
        next_node_id = self.node_tree.tree.get_next_uncle(node_id)

        if next_node_id and self.node_tree.is_ancestor_of_root(next_node_id):
            return next_node_id

    def get_next_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        return self.get_next_from(node_id)

    def get_next_non_descendant_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        return self.node_tree.tree.get_next_uncle(node_id)

    def get_previous_from(self, node_id: NodeId) -> Optional[NodeId]:
        if previous_sibling_id := self.node_tree.tree.get_previous_sibling(node_id):
            last_child_id = None
            for last_child_id in self.node_tree.tree.get_last_descendants(previous_sibling_id):
                if not self.node_tree.is_expanded(last_child_id):
                    return last_child_id
            else:
                return last_child_id
        elif (parent_node := self.node_tree.tree.get_parent(node_id)) not in (self.node_tree.root_node, None):
            return parent_node

    def get_previous_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        return self.get_previous_from(node_id)

    def get_next_visible_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        while node_id := self.get_next_from(node_id):
            if self.filter.is_visible(node_id):
                return node_id

    def select_next_visible_node(self):
        next_id = self.get_next_visible_node()
        if next_id:
            self.selected_node_id = next_id

    def get_previous_visible_node(self) -> Optional[NodeId]:
        node_id = self.selected_node_id
        while node_id := self.get_previous_from(node_id):
            if self.filter.is_visible(node_id):
                return node_id
