
from typing import *

from changes import change as ch
import nodes.node as nd
from nodes.node import NodeId
from enums import TreeLink
from ui.node_path import BreadCrumb
from ui.ui import UIState


class ChangesForAction:
    def __init__(self, ui_state: UIState):
        self.node_tree = ui_state.node_tree
        self.node_path = ui_state.node_path

    def dive_into_node(self, changes: List[ch.Change], node_id: NodeId):
        changes.append(ch.SetRootNode(node_id))
        if not (first_child_id := self.node_tree.tree.get_first_child(node_id)):
            first_child_id = nd.get_next_available_temp_id()
            changes.append(ch.InsertNewNodeAfter(first_child_id, node_id, TreeLink.Parent))
        changes.append(ch.NewSelection(first_child_id))

        node_path = self.node_path
        relative_path = self.node_tree.tree.get_ancestors_relative_to(node_id, self.node_tree.root_node)
        relative_path.reverse()
        breadcrumb = BreadCrumb(self.node_tree.root_node, node_id)
        node_path.push(breadcrumb, relative_path)
        changes.append(ch.SetNodePath(node_path))
