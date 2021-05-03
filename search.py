
from typing import *

from nodes.node_types import NodeId
from ui.text_editor import TextEditor


class Search:
    editor: TextEditor
    matched_node_ids: Optional[List[NodeId]]

    def __init__(self):
        self.editor = TextEditor('')
        self.matched_node_ids = None

    def is_visible(self, node_id: NodeId):
        return self.matched_node_ids is None or node_id in self.matched_node_ids
