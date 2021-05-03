
import asyncio

from asciimatics.screen import ManagedScreen, Screen as ScreenApi

from globals import change_notifier

import consts
from changes.change_action import ActionToChange
from changes.handle_change import ChangeHandler
from database import async_db_commands, db, init_db
import enums
from nodes.node_tree import NodeTree
from search import Search
from ui.edit import Edit
from ui.selection import Selection
from ui.ui import UIState
from view.layout import Layout
from view.render import RenderLayout
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider
from view_data_provider.search_data_provider import SearchDataProvider
from view.ui_components import get_layout

from actions.action_events import ActionEventAsync


class Screen:
    screen_api: ScreenApi

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


async def action_event_loop(
        ui_state: UIState,
        screen: Screen,
        layout: Layout,
):
    screen.screen_api.print_at(str(ui_state.mode), 0, screen.height - 2, colour=7)

    action_events = ActionEventAsync(ui_state)
    action_to_change = ActionToChange(ui_state.node_tree, ui_state.selection, ui_state.node_edit, screen, ui_state)

    layout_renderer = RenderLayout(screen.screen_api, layout)
    layout_renderer.render_layout()

    while True:
        next_action = await action_events.next_action()
        if not next_action:
            continue
        change_action = action_to_change.determine_changes(next_action)

        change_notifier.notify_changes(change_action.changes)

        if ui_state.screen_needs_reset:
            screen.screen_api.clear()
            ui_state.screen_needs_reset = False

        layout_renderer.render_layout()

        screen.screen_api.print_at(str(ui_state.mode), 0, screen.height - 2, colour=7)
        screen.screen_api.print_at(f'Width: {screen.width}', 0, screen.height - 1, colour=7)
        screen.screen_api.refresh()


async def main(db_path=None):
    db_path = db_path or consts.DB_PATH
    await init_db.init_if_needed(db_path)

    db_commands = async_db_commands.AsyncDbCommands(db_path)
    db_commands.process_database_queue()

    all_nodes = await db_commands.enqueue_database_transaction(db.get_all_nodes)

    node_tree = NodeTree(all_nodes)
    search = Search()
    selection = Selection(node_tree, search)
    selection.selected_node_id = node_tree.first_node
    node_edit = Edit()

    with ManagedScreen() as _screen:

        screen = Screen(_screen)

        ui_state = UIState(enums.Mode.Navigate, selection, node_edit, search, node_tree, screen)
        ui_state.mode = enums.Mode.Navigate

        node_tree_data_provider = NodeTreeDataProvider(ui_state)
        breadcrumbs_data_provider = BreadcrumbsDataProvider(ui_state)
        search_data_provider = SearchDataProvider(ui_state)

        layout = get_layout(
            width=screen.width,
            height=screen.height - 2,  # Reserve two lines at the bottom for some extra logging
            breadcrumbs_data_provider=breadcrumbs_data_provider,
            node_tree_data_provider=node_tree_data_provider,
            search_data_provider=search_data_provider,
        )

        # This variable isn't used, but we need a reference to it to keep it alive
        change_handler = ChangeHandler(ui_state, screen, db_commands)
        id(change_handler)  # Use it in a noop to make static checking happy

        await action_event_loop(ui_state, screen, layout)


if __name__ == '__main__':
    import os
    import sys

    db_path_arg = None
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
        db_path_arg = os.path.join(consts.DB_DIR, db_name) + '.sqlite'

    asyncio.run(main(db_path_arg))
