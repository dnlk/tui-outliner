
from keyboard_events import KeyboardEventAsync
from windows_keyboard_events import WindowsKeyEventReader
from enums import Mode
from keys import Key, KeyEvent, Shift, Control, Alt
import actions
from ui import UIState


class ActionEventAsync:
    def __init__(self, ui_state):
        self.keyboard_event_async = KeyboardEventAsync(WindowsKeyEventReader())
        self.ui_state: UIState = ui_state

    def _get_navigate_action(self, key_event: KeyEvent):

        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.EditNode)
        elif key_event == Key.DOWN:
            return actions.NavigateDown(1)
        elif key_event == Key.UP:
            return actions.NavigateUp(1)
        elif key_event == (Key.DOWN, Control):
            return actions.MoveSelectedNodeDown()
        elif key_event == (Key.UP, Control):
            return actions.MoveSelectedNodeUp()
        elif key_event == Key.TAB:
            return actions.TabNode()
        elif key_event == (Key.TAB, Shift):
            return actions.UntabNode()
        elif key_event == Key.A:
            return actions.NewNodeNextSibling()
        elif key_event == Key.DELETE:
            return actions.DeleteSelectedNodeAndSelectNext()
        elif key_event == Key.BACK:
            return actions.DeleteSelectedNodeAndSelectPrevious()
        else:
            print(f'Unhandled key event: {key_event}')

    def _get_edit_action(self, key_event: KeyEvent):
        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.Navigate)
        elif key_event == Key.LEFT:
            return actions.CursorDecrement()
        elif key_event == Key.RIGHT:
            return actions.CursorIncrement()
        elif key_event == Key.DOWN:
            return actions.CursorRowIncrement()
        elif key_event == Key.UP:
            return actions.CursorRowDecrement()
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
