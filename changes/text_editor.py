
from common_imports import *

from changes import change as ch
from changes.change import Change, ChangeNotifier
from datastructures.text_editor import TextEditor
from enums import Mode


class TextEditorChangeHandler:
    mode: Mode

    def __init__(self, change_notifier: ChangeNotifier, mode: Mode, text_editor: TextEditor, text_edited_notify):
        self.mode = mode
        self.text_editor = text_editor
        self.text_edited_notify = text_edited_notify or (lambda: None)

        change_notifier.register(self, ch.AddCharacter)
        change_notifier.register(self, ch.RemoveCharacter)
        change_notifier.register(self, ch.SetCursor)
        change_notifier.register(self, ch.ClearText)
        change_notifier.register(self, ch.NewParagraph)
        change_notifier.register(self, ch.MergeParagraphs)

    def handle_change(self, change: Change):
        if isinstance(change, ch.AddCharacter):
            self.text_editor.add_character(change.char, change.cursor)
            self.text_edited_notify()
        elif isinstance(change, ch.RemoveCharacter):
            self.text_editor.remove_character(change.cursor)
            self.text_edited_notify()
        elif isinstance(change, ch.SetCursor):
            self.text_editor.cursor = change.cursor
        elif isinstance(change, ch.ClearText):
            self.text_editor.reset('')
            self.text_edited_notify()
        elif isinstance(change, ch.NewParagraph):
            self.text_editor.split_paragraph(change.cursor, change.new_id)
        elif isinstance(change, ch.MergeParagraphs):
            self.text_editor.paragraphs.merge(change.p_id1, change.p_id2)
