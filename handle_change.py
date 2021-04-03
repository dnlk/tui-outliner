
import change as ch
from change_action import ChangeAction
import db
from enums import TreeLink
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
            self.ui_state.mode = change.mode

            # Hardcoded the rules for determining the drawable width of the node :(
            screen_width = self.screen.width
            left_padding = 3 + 2 * self.node_tree.get_depth(self.selection.selected_node_id)
            edit_width = screen_width - left_padding

            self.ui_state.node_edit.set_node(self.selection.selected_node_id, self._get_selected_node(), edit_width)
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
            self.ui_state.node_edit.text_editor.add_character(change.char, change.cursor)
        elif isinstance(change, ch.RemoveCharacter):
            self.ui_state.node_edit.text_editor.remove_character(change.cursor)
        elif isinstance(change, ch.SetCursor):
            self.ui_state.node_edit.text_editor.cursor = change.cursor
        elif isinstance(change, ch.SetNodeText):
            node = self._get_selected_node()
            node.text = change.text
        else:
            print(f'Unhandled change: {change}')
