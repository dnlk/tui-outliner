
from typing import List
import sqlite3

from node_tree import NodeTree
import db
from selection import Selection
from transaction import NodeTransaction


class StateController:
    node_tree: NodeTree

    def __init__(self, conn: sqlite3.Connection, node_tree: NodeTree, selection: Selection):
        self.node_tree = node_tree
        self.conn = conn
        self.selection = selection

    def apply_node_tree_transactions(self, node_transactions: List[NodeTransaction]):
        for transaction in node_transactions:
            self.node_tree.apply_transaction(transaction)
            db.apply_node_tree_transaction(self.conn, transaction)
            self.selection.apply_transaction(transaction)
