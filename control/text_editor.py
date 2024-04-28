
from common_imports import *

from actions import actions as act
from actions.notifier import ActionNotifier, ChangeAction
from changes import change as ch
from datastructures.text_editor import Cursor, TextEditor
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
        action_notifier.register(self, act.CursorIncrementWord)
        action_notifier.register(self, act.CursorDecrementWord)
        action_notifier.register(self, act.CursorRowIncrement)
        action_notifier.register(self, act.CursorRowDecrement)
        action_notifier.register(self, act.RemoveCharacterBeforeCursor)
        action_notifier.register(self, act.RemoveCharacterAtCursor)
        action_notifier.register(self, act.NewParagraphAtCursor)

    @property
    def paragraphs(self):
        return self.text_editor.paragraphs

    @property
    def cursor(self):
        return self.text_editor.cursor

    @property
    def calculate_cursor(self):
        return self.text_editor.calculate_cursor

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
        elif isinstance(action, act.CursorIncrementWord):
            new_cursor = self.text_editor.calculate_cursor.get_incr_word_cursor()
            changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.CursorDecrementWord):
            new_cursor = self.text_editor.calculate_cursor.get_decr_word_cursor()
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
            if self.calculate_cursor.is_origin():
                # At the beginning - do nothing
                pass
            elif self.calculate_cursor.is_p_origin():
                # At the beginning of a paragraph - merge this with the previous paragraph
                p_id2 = self.cursor.p_id
                p_id1 = self.paragraphs.get_previous(p_id2)
                new_offset = len(self.paragraphs[p_id1].text)
                new_cursor = Cursor(p_id1, new_offset)
                changes.append(ch.MergeParagraphs(p_id1, p_id2).with_mode(self.mode))
                changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
            else:
                new_cursor = self.text_editor.calculate_cursor.get_decr_cursor()
                changes.append(ch.SetCursor(new_cursor).with_mode(self.mode))
                changes.append(ch.RemoveCharacter(new_cursor).with_mode(self.mode))
        elif isinstance(action, act.RemoveCharacterAtCursor):
            if self.calculate_cursor.is_end():
                pass
            elif self.calculate_cursor.is_p_end():
                # At the end of a paragraph - merge with the next paragraph
                p_id1 = self.cursor.p_id
                p_id2 = self.paragraphs.get_next(p_id1)
                changes.append(ch.MergeParagraphs(p_id1, p_id2).with_mode(self.mode))
            else:
                cursor = self.text_editor.cursor
                changes.append(ch.RemoveCharacter(cursor).with_mode(self.mode))
        elif isinstance(action, act.NewParagraphAtCursor):
            if self.mode == Mode.EditNode:
                cursor = self.text_editor.cursor
                new_id = self.text_editor.paragraphs.make_unique_id()
                changes.append(ch.NewParagraph(cursor, new_id).with_mode(self.mode))
                changes.append(ch.SetCursor(Cursor(new_id, 0)).with_mode(self.mode))

        return ChangeAction(changes, action)
