
from datastructures.text_editor import TextEditor


class Edit:
    def __init__(self):
        self.node = None
        self.text_editor: TextEditor = None

    def set_node(self, node_id, node):
        self.node_id = node_id
        self.node = node
        self.text_editor = TextEditor(node.text)
