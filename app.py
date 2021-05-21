
import asyncio

from asciimatics.screen import ManagedScreen, Screen as ScreenApi

import globals as gls

from actions.notifier import ActionNotifier
import consts
from changes.change import ChangeNotifier
from changes.handle_change import ChangeHandler
from changes.node_filter import NodeFilterChangeHandler
from changes.text_editor import TextEditorChangeHandler
from control.change_action import ActionToChange
from control.node_tree import NodeTreeController
from control.node_filter import NodeFilterController
from control.text_editor import TextEditorController
from data.data import Data
from database import async_db_commands, db, init_db
import enums
from nodes.node_tree import NodeTree
from filter import Filter
from ui.edit import Edit
from ui.selection import Selection
from ui.ui import UIState
from view.layout import Layout
from view.render import RenderLayout
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.filter_data_provider import FilterDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider
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


async def process_changes(
    change_queue: asyncio.Queue,
    change_notifier: ChangeNotifier
):
    while True:
        next_change_set = await change_queue.get()
        if next_change_set.changes:
            change_notifier.notify_changes(next_change_set.changes)
            gls.null_event_required = True


async def action_event_loop(
        ui_state: UIState,
        screen: Screen,
        layout: Layout,
        action_notifier: ActionNotifier,
        change_queue: asyncio.Queue,
):
    screen.screen_api.print_at(str(ui_state.mode), 0, screen.height - 2, colour=7)

    action_events = ActionEventAsync(ui_state)

    layout_renderer = RenderLayout(screen.screen_api, layout)
    layout_renderer.render_layout()

    while True:
        next_action = await action_events.next_action()
        if not next_action:
            continue

        change_action = action_notifier.notify_action(next_action)
        change_queue.put_nowait(change_action)

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
    _filter = Filter()
    selection = Selection(node_tree, _filter)
    selection.selected_node_id = node_tree.first_node
    node_edit = Edit()

    with ManagedScreen() as _screen:

        screen = Screen(_screen)

        ui_state = UIState(enums.Mode.Navigate, selection, node_edit, _filter, node_tree, screen)
        ui_state.mode = enums.Mode.Navigate

        change_queue = asyncio.Queue()

        node_edit_text_data = Data[str](change_queue, '')
        filter_text_data = Data[str](change_queue, '')

        node_tree_data_provider = NodeTreeDataProvider(ui_state)
        breadcrumbs_data_provider = BreadcrumbsDataProvider(ui_state)
        filter_data_provider = FilterDataProvider(ui_state)

        action_notifier = ActionNotifier()
        ActionToChange(action_notifier, ui_state)
        TextEditorController(action_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, ui_state)
        TextEditorController(action_notifier, enums.Mode.Filter, ui_state.filter.editor, ui_state)
        NodeTreeController(action_notifier, ui_state)

        NodeFilterController(action_notifier, filter_text_data)

        change_notifier = ChangeNotifier()
        ChangeHandler(change_notifier, ui_state, db_commands)
        TextEditorChangeHandler(change_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, node_edit_text_data)
        TextEditorChangeHandler(change_notifier, enums.Mode.Filter, ui_state.filter.editor, filter_text_data)
        NodeFilterChangeHandler(change_notifier, ui_state, db_commands)

        layout = get_layout(
            width=screen.width,
            height=screen.height - 2,  # Reserve two lines at the bottom for some extra logging
            breadcrumbs_data_provider=breadcrumbs_data_provider,
            node_tree_data_provider=node_tree_data_provider,
            filter_data_provider=filter_data_provider,
            change_notifier=change_notifier
        )

        asyncio.create_task(process_changes(change_queue, change_notifier))

        await action_event_loop(ui_state, screen, layout, action_notifier, change_queue)


if __name__ == '__main__':
    import os
    import sys

    db_path_arg = None
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
        db_path_arg = os.path.join(consts.DB_DIR, db_name) + '.sqlite'

    asyncio.run(main(db_path_arg))
