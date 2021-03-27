
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
    def __init__(self, node_tree: NodeTree, selection: Selection, node_edit: Edit):
        self.node_tree = node_tree
        self.selection = selection
        self.node_edit = node_edit

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
            cursor = self.node_edit.cursor_index
            changes.append(ch.AddCharacter(cursor, action.char))
        elif action.is_type(act.FinishEditing):
            changes.append(ch.ChangeMode(Mode.Navigate))
            changes.append(ch.SetNodeText(self.node_edit.node_id, self.node_edit.text))
        elif action.is_type(act.SetCursor):
            changes.append(ch.SetCursor(action.cursor_pos))
        elif action.is_type(act.RemoveCharacterBeforeCursor):
            cursor = self.node_edit.cursor_index
            if cursor > 0:
                changes.append(ch.RemoveCharacter(cursor - 1))
        elif action.is_type(act.RemoveCharacterAtCursor):
            cursor = self.node_edit.cursor_index
            if cursor < len(self.node_edit.text):
                changes.append(ch.RemoveCharacter(cursor + 1))
        else:
            print(f'Unhandled action: {action}')

        return ChangeAction(changes, action)
