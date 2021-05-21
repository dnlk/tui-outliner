
from typing import *

from changes import change as ch
from changes.change import Change, ChangeNotifier
from data.data import Data
from datastructures.text_editor import TextEditor
from enums import Mode


class TextEditorChangeHandler:
    mode: Mode

    def __init__(self, change_notifier: ChangeNotifier, mode: Mode, text_editor: TextEditor, text_editor_data: Data[str]):
        self.mode = mode
        self.text_editor = text_editor
        self.text_editor_data = text_editor_data

        change_notifier.register(self, ch.AddCharacter)
        change_notifier.register(self, ch.RemoveCharacter)
        change_notifier.register(self, ch.SetCursor)

    def handle_change(self, change: Change):
        if isinstance(change, ch.AddCharacter):
            self.text_editor.add_character(change.char, change.cursor)
            self.text_editor_data.set_data(self.text_editor.get_data())
        elif isinstance(change, ch.RemoveCharacter):
            self.text_editor.remove_character(change.cursor)
            self.text_editor_data.set_data(self.text_editor.get_data())
        elif isinstance(change, ch.SetCursor):
            self.text_editor.cursor = change.cursor
