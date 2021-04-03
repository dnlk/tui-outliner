
from enums import Mode

from edit import Edit


class UIState:
    mode: Mode
    node_edit: Edit

    def __init__(self, mode: Mode, selection, node_edit):
        self.mode = mode
        self.selection = selection
        self.node_edit = node_edit
