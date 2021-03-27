
class Edit:

    def __init__(self):
        self.node = None
        self.text = None
        self.cursor_index = None

    def set_node(self, node_id, node):
        self.node_id = node_id
        self.node = node
        self.text = node.text
        self.cursor_index = len(node.text)

    def add_string(self, s):
        self.text = self.text[:self.cursor_index] + s + self.text[self.cursor_index:]
        self.cursor_index += len(s)

    def remove_character(self, index):

        self.text = self.text[:index] + self.text[index + 1:]

        cursor = self.cursor_index
        if index < cursor:
            self.cursor_index -= 1
        elif cursor > len(self.text):
            self.cursor_index -= 1

    def get_edit_text(self):
        return self.text

    def set_text(self, text: str):
        self.text = text
