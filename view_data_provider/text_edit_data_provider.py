
from common_imports import *

from datastructures.text_editor import TextEditor
from enums import Mode
from ui.ui import UIState
from view.color import Color
from view.text import Line, simple_line, line_with_cursor


class TextEditDataProvider:
    def __init__(self, editor: TextEditor, ui_state: UIState, mode: Mode):
        self.mode = mode
        self.editor = editor
        self.ui_state = ui_state
        self.width = 0

    def set_width(self, width: int):
        self.width = width

    def get_lines(self) -> List[Line]:
        if self.ui_state.mode == self.mode:
            cursor_pos = self.editor.cursor.offset
            return [
                simple_line('-' * self.width, 0, Color.Black, Color.White),
                line_with_cursor(
                    self.editor.get_data(),
                    0,
                    cursor_pos,
                    Color.Black,
                    Color.White,
                    Color.White,
                    Color.Black,
                )
            ]
        else:
            return []

    def num_lines(self) -> int:
        if self.ui_state.mode == self.mode:
            return 2
        else:
            return 0
