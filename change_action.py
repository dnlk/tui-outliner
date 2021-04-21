
from typing import List

import actions as act
import change as ch
from edit import Edit
from enums import TreeLink, Mode
import node as nd
from node_path import BreadCrumb
from node_tree import NodeTree
from ui import UIState
from selection import Selection


class ChangeAction:
    def __init__(self, changes: List[ch.Change], action: act.Action):
        self.changes = changes
        self.action = action


class ActionToChange:

    node_edit: Edit

    def __init__(self, node_tree: NodeTree, selection: Selection, node_edit: Edit, screen, ui_state: UIState):
        self.node_tree = node_tree
        self.selection = selection
        self.node_edit = node_edit
        self.screen = screen
        self.ui_state = ui_state

    def determine_changes(self, action) -> ChangeAction:
        changes: List[ch.Change] = []
        if action.is_type(act.ChangeMode):
            changes.append(ch.ChangeMode(action.mode))
        elif action.is_type(act.NavigateUp):
            if new_selected_node := self.selection.get_previous_node():
                changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.NavigateDown):
            if new_selected_node := self.selection.get_next_node():
                changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.MoveSelectedNodeUp):
            node_id = self.selection.selected_node_id
            if prev_node_id := self.selection.get_previous_node():
                if prev_prev := self.node_tree.tree.get_previous(prev_node_id):
                    prev_prev_id, prev_prev_link = prev_prev
                    changes.append(ch.MoveNode(node_id, prev_prev_id, prev_prev_link))
        elif action.is_type(act.MoveSelectedNodeDown):
            if next_node_id := self.selection.get_next_non_descendant_node():
                if self.node_tree.is_expanded(next_node_id) and self.node_tree.tree.get_first_child(next_node_id):
                    link_type = TreeLink.Parent
                else:
                    link_type = TreeLink.Sibling
                changes.append(ch.MoveNode(self.selected_id, next_node_id, link_type))
        elif action.is_type(act.NewNodeNextSibling):
            new_node_id = nd.get_next_available_temp_id()
            changes.append(ch.InsertNewNodeAfter(new_node_id, self.selection.selected_node_id, TreeLink.Sibling))
            changes.append(ch.NewSelection(new_node_id))
        elif action.is_type(act.TabNode):
            selected_node_id = self.selected_id
            if previous := self.node_tree.tree.get_previous(selected_node_id):
                previous_id, link_type = previous
                if link_type == TreeLink.Sibling:
                    if not self.node_tree.is_expanded(previous_id):
                        changes.append(ch.SetExpanded(previous_id, True))
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
            remaining_width = self.ui_state.get_remaining_text_width_for_selected_node()
            new_cursor = self.node_edit.text_editor.calculate_cursor.get_cursor_for_incr_row(remaining_width)
            changes.append(ch.SetCursor(new_cursor))
        elif action.is_type(act.CursorRowDecrement):
            remaining_width = self.ui_state.get_remaining_text_width_for_selected_node()
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
        elif (action.is_type(act.DeleteSelectedNodeAndSelectNext) or
              action.is_type(act.DeleteSelectedNodeAndSelectPrevious)):
            selected_node = self.selection.selected_node_id
            if not self.node_tree.is_only_descendant_of_root(selected_node):
                changes.append(ch.DeleteNode(selected_node))

                if action.is_type(act.DeleteSelectedNodeAndSelectNext):
                    first_selection_attempt = self.selection.get_next_non_descendant_node
                    second_selection_attempt = self.selection.get_previous_node
                else:
                    first_selection_attempt = self.selection.get_previous_node
                    second_selection_attempt = self.selection.get_next_non_descendant_node

                if next_selected_node := first_selection_attempt():
                    changes.append(ch.NewSelection(next_selected_node))
                elif prev_selected_node := second_selection_attempt():
                    changes.append(ch.NewSelection(prev_selected_node))
                else:
                    assert False, 'Failed to determine next or previous selection'
        elif action.is_type(act.DiveIntoSelectedNode):
            changes.append(ch.SetRootNode(self.selected_id))
            if not (first_child_id := self.node_tree.tree.get_first_child(self.selected_id)):
                first_child_id = nd.get_next_available_temp_id()
                changes.append(ch.InsertNewNodeAfter(first_child_id, self.selected_id, TreeLink.Parent))
            changes.append(ch.NewSelection(first_child_id))

            node_path = self.ui_state.node_path
            relative_path = self.node_tree.tree.get_ancestors_relative_to(self.selected_id, self.node_tree.root_node)
            relative_path.reverse()
            breadcrumb = BreadCrumb(self.node_tree.root_node, self.selected_id)
            node_path.push(breadcrumb, relative_path)
            changes.append(ch.SetNodePath(node_path))
        elif action.is_type(act.ClimbOutOfNode):
            node_path = self.ui_state.node_path
            if node_path.breadcrumbs:
                breadcrumb = node_path.pop()
                changes.append(ch.SetRootNode(breadcrumb.root_node_id))
                changes.append(ch.NewSelection(breadcrumb.selected_node_id))
                changes.append(ch.SetNodePath(node_path))
        elif action.is_type(act.ToggleNodeExpanded):
            changes.append(ch.SetExpanded(self.selected_id, not self.selected_node.expanded))
        elif action.is_type(act.ScrollDown):
            changes.append(ch.ScrollAdjust(1))
        elif action.is_type(act.ScrollUp):
            changes.append(ch.ScrollAdjust(-1))
        else:
            print(f'Unhandled action: {action}')

        return ChangeAction(changes, action)

    @property
    def selected_id(self):
        return self.selection.selected_node_id

    @property
    def selected_node(self):
        return self.node_tree.get_node(self.selected_id)
