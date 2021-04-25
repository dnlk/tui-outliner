
from copy import deepcopy
from enums import Mode

from nodes.node_tree import NodeTree
from ui.edit import Edit
from ui.node_path import NodePath
from ui.selection import Selection


class UIState:
    mode: Mode
    node_edit: Edit
    screen_needs_reset: bool = False
    selection: Selection
    node_tree: NodeTree

    def __init__(self, mode: Mode, selection: Selection, node_edit: Edit, node_tree: NodeTree, screen):
        self.mode = mode
        self.selection = selection
        self.node_edit = node_edit
        self.node_tree = node_tree
        self.screen = screen

        node_path = NodePath()
        node_path.node_ids = [self.node_tree.root_node]
        self._node_path = node_path

    def refresh_screen(self):
        self.screen_needs_reset = True

    def get_remaining_text_width_for_selected_node(self):
        node_depth = self.node_tree.get_depth(self.selection.selected_node_id)
        return self.screen.remaining_width_for_node_depth(node_depth)

    @property
    def node_path(self) -> NodePath:
        return deepcopy(self._node_path)

    @node_path.setter
    def node_path(self, node_path: NodePath):
        self._node_path = node_path
