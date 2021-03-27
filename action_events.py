
from keyboard_events import KeyboardEventAsync
from windows_keyboard_events import WindowsKeyEventReader
from enums import Mode
from keys import Key, KeyEvent, Shift, Control, Alt
import actions


class ActionEventAsync:
    def __init__(self, ui_state):
        self.keyboard_event_async = KeyboardEventAsync(WindowsKeyEventReader())
        self.ui_state = ui_state

    def _get_navigate_action(self, key_event: KeyEvent):

        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.EditNode)
        elif key_event == Key.DOWN:
            return actions.NavigateDown(1)
        elif key_event == Key.UP:
            return actions.NavigateUp(1)
        elif key_event == Key.TAB:
            return actions.TabNode()
        elif key_event == (Key.TAB, Shift):
            return actions.UntabNode()
        elif key_event == Key.A:
            return actions.NewNodeNextSibling()
        else:
            print(f'Unhandled key event: {key_event}')

    def _get_edit_action(self, key_event: KeyEvent):
        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.Navigate)
        elif key_event == Key.LEFT:
            old_cursor_pos = self.ui_state.node_edit.cursor_index
            new_cursor_pos = max(0, old_cursor_pos - 1)
            return actions.SetCursor(new_cursor_pos)
        elif key_event == Key.RIGHT:
            old_cursor_pos = self.ui_state.node_edit.cursor_index
            text = self.ui_state.node_edit.text
            new_cursor_pos = min(len(text), old_cursor_pos + 1)
            return actions.SetCursor(new_cursor_pos)
        elif key_event == Key.BACK:
            return actions.RemoveCharacterBeforeCursor()
        elif key_event == Key.DELETE:
            return actions.RemoveCharacterAtCursor()
        elif key_event == Key.SPACE:
            return actions.AddCharacterToEdit(' ')
        elif key_event == Key.RETURN:
            return actions.FinishEditing()
        elif key_event.char:
            return actions.AddCharacterToEdit(key_event.char)
        else:
            print(f'Unhandled key event: {key_event}')

    async def next_action(self):
        next_key = await self.keyboard_event_async.next_key()

        print(next_key)

        if self.ui_state.mode == Mode.Navigate:
            return self._get_navigate_action(next_key)
        elif self.ui_state.mode == Mode.EditNode:
            return self._get_edit_action(next_key)
