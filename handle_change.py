
import change as ch
from change_action import ChangeAction
import db
from enums import Mode,TreeLink
from node import NodeData
from node_tree import NodeTree, NodeContext
from selection import Selection
from ui import UIState


class ChangeHandler:
    def __init__(self, node_tree: NodeTree, selection: Selection, ui_state: UIState, screen, conn):
        self.node_tree = node_tree
        self.selection = selection
        self.ui_state = ui_state
        self.screen = screen
        self.conn = conn

    def _get_selected_node(self):
        if selected_node := self.selection.selected_node_id:
            return self.node_tree.get_node(selected_node)

    def handle(self, change_action: ChangeAction):
        for change in change_action.changes:
            self.handle_change(change)

    def handle_change(self, change: ch.Change):
        if isinstance(change, ch.ChangeMode):
            if change.mode == Mode.EditNode:
                self.ui_state.node_edit.set_node(self.selection.selected_node_id, self._get_selected_node())
            self.ui_state.mode = change.mode
        elif isinstance(change, ch.NewSelection):
            assert change.node_id is not None
            self.selection.selected_node_id = change.node_id
        elif isinstance(change, ch.InsertNewNodeAfter):
            node_context = NodeContext(
                change.node_id,
                NodeData(),
                change.previous_id,
                change.link_type,
            )
            self.node_tree.insert_node(node_context)

            db.create_node_after(self.conn.cursor(), change.node_id, change.previous_id, change.link_type)
            self.conn.commit()
        elif isinstance(change, ch.MoveNode):
            self.node_tree.tree.move_after(change.id, change.previous_node_id, change.link_type)
            db.move_after(self.conn.cursor(), change.id, change.previous_node_id, change.link_type)
            self.conn.commit()
        elif isinstance(change, ch.AddCharacter):
            self.ui_state.node_edit.text_editor.add_character(change.char, change.cursor)
        elif isinstance(change, ch.RemoveCharacter):
            self.ui_state.node_edit.text_editor.remove_character(change.cursor)
        elif isinstance(change, ch.SetCursor):
            self.ui_state.node_edit.text_editor.cursor = change.cursor
        elif isinstance(change, ch.SetNodeText):
            node_id = self.selection.selected_node_id
            node = self.node_tree.get_node(node_id)
            db.update_node_text(
                self.conn.cursor(),
                node_id,
                change.text
            )
            self.conn.commit()
            node.text = change.text
        elif isinstance(change, ch.DeleteNode):
            self.node_tree.delete_node(change.node_id)
            db.delete_node(self.conn.cursor(), change.node_id)
            self.conn.commit()
        elif isinstance(change, ch.SetRootNode):
            self.node_tree.root_node = change.node_id
        elif isinstance(change, ch.SetExpanded):
            self.node_tree.set_expanded(change.node_id, change.expanded)
            db.update_node_expanded(self.conn.cursor(), change.node_id, change.expanded)
            self.conn.commit()
        else:
            print(f'Unhandled change: {change}')
