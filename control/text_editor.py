
from typing import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from datastructures.text_editor import TextEditor
from enums import Mode
from ui.ui import UIState


class TextEditorController:

    def __init__(self, action_notifier: ActionNotifier, mode: Mode, text_editor: TextEditor, ui_state: UIState):
        self.mode = mode
        self.text_editor = text_editor
        self.ui_state = ui_state
        self.node_edit = ui_state.node_edit

        action_notifier.register(self, act.AddCharacterToEdit)
        action_notifier.register(self, act.CursorIncrement)
        action_notifier.register(self, act.CursorDecrement)
        action_notifier.register(self, act.CursorRowIncrement)
        action_notifier.register(self, act.CursorRowDecrement)
        action_notifier.register(self, act.RemoveCharacterBeforeCursor)
        action_notifier.register(self, act.RemoveCharacterAtCursor)

    def determine_changes_from_action(self, action: act.Action) -> ChangeAction:
        changes: List[ch.Change] = []
        if isinstance(action, act.AddCharacterToEdit):
            cursor = self.text_editor.cursor
            new_cursor = self.text_editor.cursor.with_offset_incr(1)
            changes.append(ch.AddCharacter(cursor, action.char).with_mode(self.mode))
            changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.CursorIncrement):
            new_cursor = self.text_editor.calculate_cursor.get_incr_cursor()
            changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.CursorDecrement):
            new_cursor = self.text_editor.calculate_cursor.get_decr_cursor()
            changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.CursorRowIncrement):
            if self.ui_state.mode == Mode.EditNode:
                remaining_width = self.ui_state.get_remaining_text_width_for_selected_node()
                new_cursor = self.node_edit.text_editor.calculate_cursor.get_cursor_for_incr_row(remaining_width)
                changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.CursorRowDecrement):
            if self.ui_state.mode == Mode.EditNode:
                remaining_width = self.ui_state.get_remaining_text_width_for_selected_node()
                new_cursor = self.node_edit.text_editor.calculate_cursor.get_cursor_for_decr_row(remaining_width)
                changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.RemoveCharacterBeforeCursor):
            assert len(self.text_editor.paragraphs) <= 1, 'Support for multiple paragraphs not implemented'

            if not self.text_editor.calculate_cursor.is_origin():
                new_cursor = self.text_editor.calculate_cursor.get_decr_cursor()
                changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
                changes.append(ch.RemoveCharacter(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.RemoveCharacterAtCursor):
            assert len(self.text_editor.paragraphs) <= 1, 'Support for multiple paragraphs not implemented'

            cursor = self.text_editor.cursor
            changes.append(ch.RemoveCharacter(cursor).with_mode(self.mode))

        return ChangeAction(changes, action)
