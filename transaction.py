
import abc

from node_types import NodeId
from node import get_next_available_temp_id
from change import NodeChange, NewSelection, Change


class NodeTransaction:
    def __init__(self, changes=None):
        self.changes = changes or []

    def append(self, change):
        self.changes.append(change)

    # def append_new_node(self, parent_id):
    #     node_id = get_next_available_temp_id()
    #     new_node_change = NewNode(node_id, parent_id)
    #     self.append(new_node_change)
    #     return new_node_change

    def append_change_node(self, node_id):
        change_node_change = NodeChange(node_id)
        self.append(change_node_change)
        return change_node_change

    def append_new_selection_change(self, node_id):
        selection_change = NewSelection(node_id)
        self.append(selection_change)
        return selection_change
