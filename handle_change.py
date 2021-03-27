
import change as ch
from change_action import ChangeAction
import db
from enums import TreeLink
from node import NodeData
from node_tree import NodeTree, NodeContext
from selection import Selection
from ui import UIState


class ChangeHandler:
    def __init__(self, node_tree: NodeTree, selection: Selection, ui_state: UIState, conn):
        self.node_tree = node_tree
        self.selection = selection
        self.ui_state = ui_state
        self.conn = conn

    def _get_selected_node(self):
        if selected_node := self.selection.selected_node_id:
            return self.node_tree.get_node(selected_node)

    def handle(self, change_action: ChangeAction):
        for change in change_action.changes:
            self.handle_change(change)

    def handle_change(self, change: ch.Change):
        if isinstance(change, ch.ChangeMode):
            self.ui_state.mode = change.mode
            self.ui_state.node_edit.set_node(self.selection.selected_node_id, self._get_selected_node())
        elif isinstance(change, ch.NewSelection):
            self.selection.selected_node_id = change.node_id
        elif isinstance(change, ch.NewNodeNextSibling):
            node_context = NodeContext(
                change.id,
                NodeData(),
                change.previous_id,
                TreeLink.Sibling,
            )
            self.node_tree.insert_node(node_context)

            db.create_node_after_as_sibling(self.conn.cursor(), change.id, change.previous_id)
        elif isinstance(change, ch.MoveNode):
            self.node_tree.tree.move_after(change.id, change.previous_node_id, change.link_type)
        elif isinstance(change, ch.AddCharacter):
            cursor = change.cursor_pos
            old_text = self.ui_state.node_edit.text
            new_text = old_text[:cursor] + change.char + old_text[cursor:]
            self.ui_state.node_edit.set_text(new_text)
            self.ui_state.node_edit.cursor_index = cursor + 1
        elif isinstance(change, ch.SetCursor):
            self.ui_state.node_edit.cursor_index = change.cursos_pos
        elif isinstance(change, ch.RemoveCharacter):
            self.ui_state.node_edit.remove_character(change.index)
        elif isinstance(change, ch.SetNodeText):
            node = self._get_selected_node()
            node.text = change.text
        else:
            print(f'Unhandled change: {change}')
