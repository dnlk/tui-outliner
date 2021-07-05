
from enums import Mode
from events.keyboard_events import KeyboardEventAsync
from events.keys import Key, KeyEvent, Shift
from ui.ui import UIState

from . import actions


class ActionEventAsync:
    def __init__(self, ui_state, screen):
        self.keyboard_event_async = KeyboardEventAsync(screen.screen_api)
        self.ui_state: UIState = ui_state

    @staticmethod
    def _get_navigate_action(key_event: KeyEvent):
        if key_event == Key.E:
            return actions.ChangeMode(Mode.EditNode)
        elif key_event == Key.F:
            return actions.ChangeMode(Mode.Filter)
        elif key_event == Key.S:
            return actions.ChangeMode(Mode.Search)
        elif key_event in (Key.J, Key.DOWN):
            return actions.NavigateDown(1)
        elif key_event in (Key.K, Key.UP):
            return actions.NavigateUp(1)
        elif key_event == (Key.J, Shift):
            return actions.MoveSelectedNodeDown()
        elif key_event == (Key.K, Shift):
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
        elif key_event in (Key.RIGHT, Key.L):
            return actions.DiveIntoSelectedNode()
        elif key_event in (Key.LEFT, Key.H):
            return actions.ClimbOutOfNode()
        elif key_event == Key.SPACE:
            return actions.ToggleNodeExpanded()
        elif key_event == Key.PERIOD:
            return actions.ScrollDown()
        elif key_event == Key.COMMA:
            return actions.ScrollUp()
        else:
            print(f'Unhandled key event: {key_event}')

    @staticmethod
    def _get_edit_action(key_event: KeyEvent):
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
        elif key_event in [
            Key.ESCAPE
        ]:
            # Ignore these keys
            return
        elif key_event.char:
            return actions.AddCharacterToEdit(key_event.char)
        else:
            print(f'Unhandled key event: {key_event}')

    @classmethod
    def _get_filter_action(cls, key_event: KeyEvent):
        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.Navigate)
        else:
            return cls._get_edit_action(key_event)

    @classmethod
    def _get_search_action(cls, key_event: KeyEvent):
        if key_event == Key.ESCAPE:
            return actions.ChangeMode(Mode.Navigate)
        elif key_event == Key.DOWN:
            return actions.NavigateDown(1)
        elif key_event == Key.UP:
            return actions.NavigateUp(1)
        else:
            return cls._get_edit_action(key_event)

    async def next_action(self):
        next_key = await self.keyboard_event_async.next_key()

        if next_key == Key.NULL:
            return actions.NoOp()
        elif self.ui_state.mode == Mode.Navigate:
            action = self._get_navigate_action(next_key)
            if action:
                action.mode_origin = Mode.Navigate
                return action
        elif self.ui_state.mode == Mode.EditNode:
            action = self._get_edit_action(next_key)
            if action:
                action.mode_origin = Mode.EditNode
                return action
        elif self.ui_state.mode == Mode.Filter:
            action = self._get_filter_action(next_key)
            if action:
                action.mode_origin = Mode.Filter
                return action
        elif self.ui_state.mode == Mode.Search:
            action = self._get_search_action(next_key)
            if action:
                action.mode_origin = Mode.Search
                return action
