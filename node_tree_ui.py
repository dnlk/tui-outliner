
from node_types import NodeId
from node_tree import NodeTree, NodeTreeChange
from transaction import NodeTransaction
from node import get_next_available_temp_id
from selection import Selection


class NodeTreeUIActions:
    node_tree_change: NodeTreeChange
    node_tree: NodeTree

    def __init__(self, node_tree: NodeTree):
        self.node_tree = node_tree
        self.node_tree_change = NodeTreeChange(node_tree)

    def tab_node(self, node_id) -> NodeTransaction:
        transaction = NodeTransaction()

        previous_sibling = self.node_tree.get_previous_sibling(node_id)
        if not previous_sibling:
            return transaction

        # parent = self.node_tree.get_parent(previous_sibling.id)

        self.node_tree_change.reparent_node_to_end_of_parent(node_id, previous_sibling.id, transaction)
        self.node_tree_change.expand_node(previous_sibling.id, transaction)

        return transaction

    def untab_node(self, node_id) -> NodeTransaction:
        transaction = NodeTransaction()

        parent = self.node_tree.get_parent(node_id)
        if parent.id == self.node_tree.root_node:
            return transaction

        return self.node_tree_change.move_node_after(node_id, parent.id, transaction)

    def new_node(self, previous_sibling_node_id: NodeId):
        transaction = NodeTransaction()
        new_node_id = self.node_tree_change.insert_node_after(previous_sibling_node_id, transaction)
        transaction.append_new_selection_change(new_node_id)
        return transaction
