
from common_imports import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from changes.changes_for_action import ChangesForAction
from ui.edit import Edit
from enums import TreeLink, Mode
from nodes import node as nd
from ui.ui import UIState


class ActionToChange:

    node_edit: Edit
    mode = Mode.All

    def __init__(self, actions_notifier: ActionNotifier, ui_state: UIState):
        self.node_tree = ui_state.node_tree
        self.selection = ui_state.selection
        self.node_edit = ui_state.node_edit
        self.screen = ui_state.screen
        self.ui_state = ui_state

        actions_notifier.register(self, act.ChangeMode)
        actions_notifier.register(self, act.NavigateUp)
        actions_notifier.register(self, act.NavigateDown)
        actions_notifier.register(self, act.MoveSelectedNodeUp)
        actions_notifier.register(self, act.MoveSelectedNodeDown)
        actions_notifier.register(self, act.NewNodeNextSibling)
        actions_notifier.register(self, act.TabNode)
        actions_notifier.register(self, act.UntabNode)
        actions_notifier.register(self, act.DeleteSelectedNodeAndSelectPrevious)
        actions_notifier.register(self, act.DeleteSelectedNodeAndSelectNext)
        actions_notifier.register(self, act.DiveIntoSelectedNode)
        actions_notifier.register(self, act.ClimbOutOfNode)
        actions_notifier.register(self, act.ToggleNodeExpanded)
        actions_notifier.register(self, act.ScrollDown)
        actions_notifier.register(self, act.ScrollUp)

        actions_notifier.register(self, act.NoOp)

    def determine_changes_from_action(self, action: act.Action) -> ChangeAction:
        changes: List[ch.Change] = []
        if action.is_type(act.ChangeMode):
            changes.append(ch.ChangeMode(action.mode))
        elif action.is_type(act.NavigateUp):
            if new_selected_node := self.selection.get_previous_visible_node():
                changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.NavigateDown):
            if new_selected_node := self.selection.get_next_visible_node():
                changes.append(ch.NewSelection(new_selected_node))
        elif action.is_type(act.MoveSelectedNodeUp):
            node_id = self.selection.selected_node_id
            if prev_node_id := self.selection.get_previous_visible_node():
                if prev_prev := self.node_tree.tree.get_previous(prev_node_id):
                    prev_prev_id, prev_prev_link = prev_prev
                    changes.append(ch.MoveNode(node_id, prev_prev_id, prev_prev_link))
        elif action.is_type(act.MoveSelectedNodeDown):
            if next_node_id := self.selection.get_next_node():
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
        elif (action.is_type(act.DeleteSelectedNodeAndSelectNext) or
              action.is_type(act.DeleteSelectedNodeAndSelectPrevious)):
            selected_node = self.selection.selected_node_id
            if not self.node_tree.is_only_descendant_of_root(selected_node):
                changes.append(ch.DeleteNode(selected_node))

                if action.is_type(act.DeleteSelectedNodeAndSelectNext):
                    selection_attempt_1 = self.selection.get_next_non_descendant_node
                    selection_attempt_2 = self.selection.get_previous_node
                else:
                    selection_attempt_1 = self.selection.get_previous_node
                    selection_attempt_2 = self.selection.get_next_non_descendant_node

                if (new_id := selection_attempt_1()) and self.node_tree.is_ancestor_of_root(new_id):
                    changes.append(ch.NewSelection(new_id))
                elif (new_id := selection_attempt_2()) and self.node_tree.is_ancestor_of_root(new_id):
                    changes.append(ch.NewSelection(new_id))
                else:
                    assert False, 'Failed to determine next or previous selection'
        elif action.is_type(act.DiveIntoSelectedNode):
            ChangesForAction(self.ui_state).dive_into_node(changes, self.selected_id)
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
        elif action.is_type(act.NoOp):
            ...
        else:
            logging.info(f'Unhandled action: {action}')

        return ChangeAction(changes, action)

    @property
    def selected_id(self):
        return self.selection.selected_node_id

    @property
    def selected_node(self):
        return self.node_tree.get_node(self.selected_id)
