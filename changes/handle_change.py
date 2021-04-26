
import globals as gls

from database.async_db_commands import AsyncDbCommands
from changes import change as ch
from changes.change_action import ChangeAction
from database import db
from enums import Mode
from nodes.node import NodeData
from nodes.node_tree import NodeContext
from ui.ui import UIState


class ChangeHandler:
    def __init__(self, ui_state: UIState, screen, db_commands: AsyncDbCommands):
        self.node_tree = ui_state.node_tree
        self.selection = ui_state.selection
        self.ui_state = ui_state
        self.screen = screen
        self.db_commands = db_commands

        gls.change_notifier.register(self, ch.ChangeMode)
        gls.change_notifier.register(self, ch.NewSelection)
        gls.change_notifier.register(self, ch.InsertNewNodeAfter)
        gls.change_notifier.register(self, ch.MoveNode)
        gls.change_notifier.register(self, ch.AddCharacter)
        gls.change_notifier.register(self, ch.RemoveCharacter)
        gls.change_notifier.register(self, ch.SetCursor)
        gls.change_notifier.register(self, ch.SetNodeText)
        gls.change_notifier.register(self, ch.DeleteNode)
        gls.change_notifier.register(self, ch.SetRootNode)
        gls.change_notifier.register(self, ch.SetExpanded)
        gls.change_notifier.register(self, ch.SetNodePath)

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

            self.db_commands.enqueue_database_transaction(
                db.create_node_after,
                args=[
                    change.node_id,
                    change.previous_id,
                    change.link_type
                ]
            )
        elif isinstance(change, ch.MoveNode):
            self.node_tree.tree.move_after(change.id, change.previous_node_id, change.link_type)
            self.db_commands.enqueue_database_transaction(
                db.move_after,
                args=[
                    change.id,
                    change.previous_node_id,
                    change.link_type
                ]
            )
        elif isinstance(change, ch.AddCharacter):
            self.ui_state.node_edit.text_editor.add_character(change.char, change.cursor)
        elif isinstance(change, ch.RemoveCharacter):
            self.ui_state.node_edit.text_editor.remove_character(change.cursor)
        elif isinstance(change, ch.SetCursor):
            self.ui_state.node_edit.text_editor.cursor = change.cursor
        elif isinstance(change, ch.SetNodeText):
            node_id = self.selection.selected_node_id
            node = self.node_tree.get_node(node_id)
            self.db_commands.enqueue_database_transaction(
                db.update_node_text,
                args=[
                    node_id,
                    change.text
                ]
            )
            node.text = change.text
        elif isinstance(change, ch.DeleteNode):
            self.node_tree.delete_node(change.node_id)
            self.db_commands.enqueue_database_transaction(
                db.delete_node,
                args=[
                    change.node_id
                ]
            )
        elif isinstance(change, ch.SetRootNode):
            self.node_tree.root_node = change.node_id
        elif isinstance(change, ch.SetExpanded):
            self.node_tree.set_expanded(change.node_id, change.expanded)
            self.db_commands.enqueue_database_transaction(
                db.update_node_expanded,
                args=[
                    change.node_id,
                    change.expanded
                ]
            )
        elif isinstance(change, ch.SetNodePath):
            self.ui_state.node_path = change.node_path
        else:
            raise Exception(f'Unhandled change: {change}')
