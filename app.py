import asyncio
import os
import sys

from common_imports import *
import consts
import globals as gls

from ext.geometry import Coord

from actions.action_events import ActionEventAsync
from actions.notifier import ActionNotifier
import changes
import control
from data.data import Data
from database import async_db_commands, db, backup, init_db
import enums
from nodes.node_tree import NodeTree
from nodes.node_types import NodeId
from filter import Filter
from screen.interface import WindowInterface
from screen.window import WindowManager, WindowType
from search import Search
from ui.edit import Edit
from ui.selection import Selection
from ui.ui import UIState
from view.color import Color
from view.layout import Layout
from view.render import RenderLayout
from view.ui_components import get_layout
import view_data_provider


class Screen:
    screen_api: WindowInterface

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
    change_notifier: changes.ChangeNotifier
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
        change_notifier: changes.ChangeNotifier,
):
    screen.screen_api.print(str(ui_state.mode), Coord(x=0, y=screen.height - 2), fg_color=Color.White, bg_color=Color.Black)

    action_events = ActionEventAsync(ui_state, screen)

    layout_renderer = RenderLayout(screen.screen_api, layout)
    layout_renderer.render_layout()

    while True:
        next_action = await action_events.next_action()
        if not next_action:
            continue

        change_action = action_notifier.notify_action(next_action)
        change_notifier.notify_changes(change_action.changes)

        if ui_state.screen_needs_reset:
            screen.screen_api.clear()
            ui_state.screen_needs_reset = False

        layout_renderer.render_layout()

        screen.screen_api.print(str(ui_state.mode), Coord(x=0, y=screen.height - 2), fg_color=Color.White, bg_color=Color.Black)
        screen.screen_api.print(f'Width: {screen.width}', Coord(x=0, y=screen.height - 1), fg_color=Color.White, bg_color=Color.Black)
        screen.screen_api.refresh()


async def main(db_path: str, window_type: WindowType):
    await init_db.init_if_needed(db_path)

    db_commands = async_db_commands.AsyncDbCommands(db_path)
    db_commands.process_database_queue()

    all_nodes = await db_commands.enqueue_database_transaction(db.get_all_nodes)

    node_tree = NodeTree(all_nodes)
    _filter = Filter()
    _search = Search(max_num_results=consts.MAX_NUM_SEARCH_RESULTS)

    selection = Selection(node_tree, _filter)
    selection.selected_node_id = node_tree.first_node
    node_edit = Edit()

    with WindowManager(window_type) as _screen:
        screen = Screen(_screen)

        ui_state = UIState(enums.Mode.Navigate, selection, node_edit, _filter, _search, node_tree, screen)
        ui_state.mode = enums.Mode.Navigate

        change_queue = asyncio.Queue()

        filter_text_data = Data[str](change_queue, '')
        search_text_data = Data[str](change_queue, '')
        selected_search_item_data = Data[NodeId](change_queue, NodeId(None))

        node_tree_data_provider = view_data_provider.NodeTreeDataProvider(ui_state)
        breadcrumbs_data_provider = view_data_provider.BreadcrumbsDataProvider(ui_state)

        action_notifier = ActionNotifier()
        control.ActionToChange(action_notifier, ui_state)
        control.TextEditorController(action_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, ui_state)
        control.NodeTreeController(action_notifier, ui_state)

        control.NodeEditController(ui_state, action_notifier)
        control.NodeFilterController(action_notifier, filter_text_data)
        control.NodeSearchController(ui_state, action_notifier, search_text_data, selected_search_item_data)

        change_notifier = changes.ChangeNotifier()
        changes.ChangeHandler(change_notifier, ui_state, db_commands)
        changes.TextEditorChangeHandler(change_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, None)
        changes.NodeFilterChangeHandler(change_notifier, ui_state, db_commands)
        changes.NodeSearchChangeHandler(change_notifier, ui_state, db_commands)

        search_result_data_provider = view_data_provider.SearchResultsDataProvider(num_max_results=consts.MAX_NUM_SEARCH_RESULTS, ui_state=ui_state)

        layout = get_layout(
            width=screen.width,
            height=screen.height - 2,  # Reserve two lines at the bottom for some diagnostics
            breadcrumbs_data_provider=breadcrumbs_data_provider,
            node_tree_data_provider=node_tree_data_provider,
            filter_text_data=filter_text_data,
            search_text_data=search_text_data,
            selected_search_item_data=selected_search_item_data,
            search_results_data_provider=search_result_data_provider,
            action_notifier=action_notifier,
            change_notifier=change_notifier,
            ui_state=ui_state,
        )

        asyncio.create_task(process_changes(change_queue, change_notifier))

        await action_event_loop(ui_state, screen, layout, action_notifier, change_notifier)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--external_window', default=WindowType.same_process, action='store_const', const=WindowType.external_process)
    parser.add_argument('-d', '--db_path', default=consts.DB_PATH)

    args = parser.parse_args()

    if args.external_window == WindowType.external_process:
        logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.INFO)
    else:
        logging.basicConfig(filename='log', encoding='utf-8', level=logging.INFO)

    if os.path.exists(consts.DB_PATH):
        backup.backup(consts.DB_PATH)

    asyncio.run(main(args.db_path, args.external_window))
