
from enums import Mode

from edit import Edit


class UIState:
    mode: Mode
    node_edit: Edit
    screen_needs_reset: bool = False

    def __init__(self, mode: Mode, selection, node_edit, node_tree, screen):
        self.mode = mode
        self.selection = selection
        self.node_edit = node_edit
        self.node_tree = node_tree
        self.screen = screen

    def refresh_screen(self):
        self.screen_needs_reset = True

    def get_remaining_text_width_for_selected_node(self):
        node_depth = self.node_tree.get_depth(self.selection.selected_node_id)
        return self.screen.remaining_width_for_node_depth(node_depth)
