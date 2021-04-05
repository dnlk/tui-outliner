
from enums import Mode

from edit import Edit


class UIState:
    mode: Mode
    node_edit: Edit
    screen_needs_reset: bool = False

    def __init__(self, mode: Mode, selection, node_edit):
        self.mode = mode
        self.selection = selection
        self.node_edit = node_edit

    def refresh_screen(self):
        self.screen_needs_reset = True
