
from common_imports import *

from changes.text_editor import TextEditorChangeHandler
from control.text_editor import TextEditorController
from datastructures.text_editor import TextEditor
from view_data_provider.text_edit_data_provider import TextEditDataProvider

from ..binding import Binding
from .lines import Lines


class TextEditorComponent(Lines):
    text: Binding[str]
    assigned_y: int
    assigned_height: int

    def __init__(self, width: int, mode, ui_state, action_notifier, change_notifier):
        self.text_editor = TextEditor('')
        data_provider = TextEditDataProvider(self.text_editor, ui_state, mode)
        super().__init__(data_provider, width)
        self.text_editor_control = TextEditorController(action_notifier, mode, self.text_editor, ui_state)
        self.text = Binding(self, self._get_text)
        self.text_editor_changes = TextEditorChangeHandler(change_notifier, mode, self.text_editor, self.text.notify)

    def _get_text(self):
        return self.text_editor.get_data()
