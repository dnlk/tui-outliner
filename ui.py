
from enums import Mode


class UIState:
    def __init__(self, mode: Mode, selection, node_edit):
        self.mode = mode
        self.selection = selection
        self.node_edit = node_edit
