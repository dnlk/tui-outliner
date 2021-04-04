
from typing import List

import actions as act
import change as ch
from edit import Edit
from enums import TreeLink, Mode
import node as nd
from node_tree import NodeTree
from selection import Selection


class ChangeAction:
    def __init__(self, changes: List[ch.Change], action: act.Action):
        self.changes = changes
        self.action = action


class ActionToChange:

    node_edit: Edit

    def __init__(self, node_tree: NodeTree, selection: Selection, node_edit: Edit, screen):
        self.node_tree = node_tree
        self.selection = selection
        self.node_edit = node_edit
        self.screen = screen

    def determine_changes(self, action) -> ChangeAction:
        changes = []
        if action.is_type(act.ChangeMode):
            changes.append(ch.ChangeMode(action.mode))
        elif action.is_type(act.NavigateUp):
            new_selected_node = self.selection.get_previous_node()
            changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.NavigateDown):
            new_selected_node = self.selection.get_next_node()
            changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.NewNodeNextSibling):
            new_node_id = nd.get_next_available_temp_id()
            changes.append(ch.NewNodeNextSibling(new_node_id, self.selection.selected_node_id))
            changes.append(ch.NewSelection(new_node_id))
        elif action.is_type(act.TabNode):
            selected_node_id = self.selection.selected_node_id
            if previous := self.node_tree.tree.get_previous(selected_node_id):
                previous_id, link_type = previous
                if link_type == TreeLink.Sibling:
                    last_child_of_sibling = self.node_tree.tree.get_last_child(previous_id)
                    if last_child_of_sibling:
                        changes.append(ch.MoveNode(selected_node_id, last_child_of_sibling, TreeLink.Sibling))
                    else:
                        changes.append(ch.MoveNode(selected_node_id, previous_id, TreeLink.Parent))
        elif action.is_type(act.UntabNode):
            selected_node_id = self.selection.selected_node_id
            if parent_id := self.node_tree.tree.get_parent(selected_node_id):
                if parent_id != self.node_tree.root_node:
                    changes.append(ch.MoveNode(selected_node_id, parent_id, TreeLink.Sibling))
        elif action.is_type(act.AddCharacterToEdit):
            cursor = self.node_edit.text_editor.cursor
            new_cursor = self.node_edit.text_editor.cursor.with_offset_incr(1)
            changes.append(ch.AddCharacter(cursor, action.char))
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.FinishEditing):
            changes.append(ch.ChangeMode(Mode.Navigate))
            changes.append(ch.SetNodeText(self.node_edit.node_id, self.node_edit.text_editor.get_data()))
        elif action.is_type(act.CursorIncrement):
            new_cursor = self.node_edit.text_editor.calculate_cursor.get_incr_cursor()
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.CursorDecrement):
            new_cursor = self.node_edit.text_editor.calculate_cursor.get_decr_cursor()
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.CursorRowIncrement):
            node_depth = self.node_tree.get_depth(self.selection.selected_node_id)
            remaining_width = self.screen.remaining_width_for_node_depth(node_depth)
            new_cursor = self.node_edit.text_editor.calculate_cursor.get_cursor_for_incr_row(remaining_width)
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.CursorRowDecrement):
            node_depth = self.node_tree.get_depth(self.selection.selected_node_id)
            remaining_width = self.screen.remaining_width_for_node_depth(node_depth)
            new_cursor = self.node_edit.text_editor.calculate_cursor.get_cursor_for_decr_row(remaining_width)
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.RemoveCharacterBeforeCursor):
            assert len(self.node_edit.text_editor.paragraphs) <= 1, 'Support for multiple paragraphs not implemented'

            if not self.node_edit.text_editor.calculate_cursor.is_origin():
                new_cursor = self.node_edit.text_editor.calculate_cursor.get_decr_cursor()
                changes.append(ch.SetCursor(new_cursor))
                changes.append(ch.RemoveCharacter(new_cursor))
        elif action.is_type(act.RemoveCharacterAtCursor):
            assert len(self.node_edit.text_editor.paragraphs) <= 1, 'Support for multiple paragraphs not implemented'

            cursor = self.node_edit.text_editor.cursor
            changes.append(ch.RemoveCharacter(cursor))

        else:
            print(f'Unhandled action: {action}')

        return ChangeAction(changes, action)
