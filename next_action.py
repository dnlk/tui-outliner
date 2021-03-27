
import actions

from enums import Mode


def next_action(ui_state, crate_tree):
    if ui_state.mode == Mode.Navigate:
        pass
    elif ui_state.mode == Mode.EditNode
        pass
    else:
        raise NotImplementedError(ui_state.mode)


async def user_actions(ui_state):

    async for keyboard_event in events.windows_keyboard_event():
        pass