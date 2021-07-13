
from common_imports import *

from datastructures.text_editor import TextEditor
from nodes.node_tree import NodeContext


class Search:
    editor: TextEditor
    matched_nodes: Optional[List[NodeContext]]

    def __init__(self, max_num_results):
        self.editor = TextEditor('')
        self.matched_nodes = None
        self.max_num_results = max_num_results

    def get_results(self) -> List[NodeContext]:
        return [] if self.matched_nodes is None else self.matched_nodes[:self.max_num_results]
