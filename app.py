
import asyncio

from ext.geometry import Coord

import globals as gls

from actions.action_events import ActionEventAsync
from actions.notifier import ActionNotifier
import consts
from changes.change import ChangeNotifier
from changes.handle_change import ChangeHandler
from changes.node_filter import NodeFilterChangeHandler
from changes.node_search import NodeSearchChangeHandler
from changes.text_editor import TextEditorChangeHandler
from control.change_action import ActionToChange
from control.node_tree import NodeTreeController
from control.node_filter import NodeFilterController
from control.node_search import NodeSearchController
from control.text_editor import TextEditorController
from data.data import Data
from database import async_db_commands, db, init_db
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
from view_data_provider.breadcrumbs_data_provider import BreadcrumbsDataProvider
from view_data_provider.node_tree_data_provider import NodeTreeDataProvider
from view_data_provider.search_results_data_provider import SearchResultsDataProvider
from view.ui_components import get_layout


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
        change_notifier: ChangeNotifier,
        change_queue: asyncio.Queue,
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

        node_tree_data_provider = NodeTreeDataProvider(ui_state)
        breadcrumbs_data_provider = BreadcrumbsDataProvider(ui_state)

        action_notifier = ActionNotifier()
        ActionToChange(action_notifier, ui_state)
        TextEditorController(action_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, ui_state)
        NodeTreeController(action_notifier, ui_state)

        NodeFilterController(action_notifier, filter_text_data)
        NodeSearchController(ui_state, action_notifier, search_text_data, selected_search_item_data)

        change_notifier = ChangeNotifier()
        ChangeHandler(change_notifier, ui_state, db_commands)
        TextEditorChangeHandler(change_notifier, enums.Mode.EditNode, ui_state.node_edit.text_editor, None)
        NodeFilterChangeHandler(change_notifier, ui_state, db_commands)
        NodeSearchChangeHandler(change_notifier, ui_state, db_commands)

        search_result_data_provider = SearchResultsDataProvider(num_max_results=consts.MAX_NUM_SEARCH_RESULTS, ui_state=ui_state)

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

        await action_event_loop(ui_state, screen, layout, action_notifier, change_notifier, change_queue)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--external_window', default=WindowType.same_process, action='store_const', const=WindowType.external_process)
    parser.add_argument('-d', '--db_path', default=consts.DB_PATH)

    args = parser.parse_args()

    asyncio.run(main(args.db_path, args.external_window))
