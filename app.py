
import asyncio

from asciimatics.screen import ManagedScreen

import enums
import db
from node_tree import NodeTree
import draw
from selection import Selection
from edit import Edit
from ui import UIState
from change_action import ActionToChange
from handle_change import ChangeHandler
import init_db
import consts

from action_events import ActionEventAsync




#
# with ManagedScreen() as screen:
#     drawer = draw.Draw(screen, selection, node_edit)
#
#     while True:
#         # screen.clear()
#         drawer.draw_node_tree(node_tree, node_tree.root_node, mode)
#         time.sleep(.1)
#         event = screen.get_event()
#
#         screen.print_at(str(mode), 0, screen.height - 2, colour=7)
#
#         if event:
#             changes: List[NodeTransaction] = []
#
#             if isinstance(event, KeyboardEvent):
#                 last_line = screen.height - 1
#                 screen.print_at('          ', 0, last_line, colour=7)
#                 screen.print_at(str(event.key_code), 0, last_line, colour=7)
#
#                 key_code = event.key_code
#                 if key_code == Screen.KEY_ESCAPE:
#                     if mode == enums.Mode.Navigate:
#                         mode = enums.Mode.EditNode
#                         node_edit.set_node(selection.get_selected_node())
#                     else:
#                         mode = enums.Mode.Navigate
#                         db.update_node_text(conn, node_edit.node.id, node_edit.text)
#                         node_edit.node.text = node_edit.text
#
#                 if mode == enums.Mode.Navigate:
#                     if key_code == Screen.KEY_UP:
#                         selection.select_previous_node()
#                     elif key_code == Screen.KEY_DOWN:
#                         selection.select_next_node()
#                     elif key_code == 13:  # Carriage return
#                         new_node_id = node.get_next_available_temp_id()
#                         changes.append(node_tree_actions.new_node(selection.selected_node_id))
#                         selection.selected_node_id = new_node_id
#                     elif key_code == Screen.KEY_TAB or key_code == 113:  # q
#                         changes.append(node_tree_actions.tab_node(selection.selected_node_id))
#                     elif key_code == Screen.KEY_BACK_TAB or key_code == 119:
#                         changes.append(node_tree_actions.untab_node(selection.selected_node_id))
#                 elif mode == enums.Mode.EditNode:
#                     if 32 <= key_code <= 126:  # ascii
#                         node_edit.add_string(chr(key_code))
#                     elif key_code == Screen.KEY_BACK:
#                         node_edit.delete_character()
#                 else:
#                     raise NotImplementedError
#
#             state_controller.apply_node_tree_transactions(changes)





async def action_event_loop(
        ui_state: UIState,
        node_tree: NodeTree,
        change_handler: ChangeHandler,
        screen,
):
    # action_events = ActionEventAsync(ui_state)
    # while True:
    #     next_action = await action_events.next_action()

    drawer = draw.Draw(screen, ui_state.selection, ui_state.node_edit, screen.width)

    drawer.draw_node_tree(node_tree, node_tree.root_node, ui_state.mode)
    screen.screen_api.print_at(str(ui_state.mode), 0, screen.height - 2, colour=7)

    action_events = ActionEventAsync(ui_state)
    action_to_change = ActionToChange(node_tree, ui_state.selection, ui_state.node_edit, screen, ui_state)

    while True:
        next_action = await action_events.next_action()
        if not next_action:
            continue
        change_action = action_to_change.determine_changes(next_action)

        for change in change_action.changes:
            change_handler.handle_change(change)

        if ui_state.screen_needs_reset:
            screen.screen_api.clear()
            ui_state.screen_needs_reset = False

        drawer.draw_node_tree(node_tree, node_tree.root_node, ui_state.mode)
        screen.screen_api.print_at(str(ui_state.mode), 0, screen.height - 2, colour=7)
        screen.screen_api.print_at(f'Width: {screen.width}', 0, screen.height - 1, colour=7)


class Screen:
    def __init__(self, screen):
        self.screen_api = screen

    @property
    def width(self):
        return self.screen_api.width

    @property
    def height(self):
        return self.screen_api.height

    def remaining_width_for_node_depth(self, depth: int):
        return self.width - (2 * depth)


async def main():
    init_db.init_if_needed(consts.DB_PATH)

    conn = db.create_connection(consts.DB_PATH)

    all_nodes = db.get_all_nodes(conn.cursor())
    node_tree = NodeTree(all_nodes)
    selection = Selection(node_tree)
    selection.selected_node_id = node_tree.first_node
    node_edit = Edit()


    with ManagedScreen() as _screen:

        screen = Screen(_screen)

        ui_state = UIState(enums.Mode.Navigate, selection, node_edit, node_tree, screen)
        ui_state.mode = enums.Mode.Navigate

        change_handler = ChangeHandler(node_tree, selection, ui_state, screen, conn)

        await action_event_loop(ui_state, node_tree, change_handler, screen)


if __name__ == '__main__':
    asyncio.run(main())
