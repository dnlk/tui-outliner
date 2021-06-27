
import asyncio

import globals as gls

from .change import Change, ChangeNotifier, UpdateNodeSearch
import consts
from database.async_db_commands import AsyncDbCommands
from database import db
from enums import Mode
from ui.ui import UIState


class NodeSearchChangeHandler:

    mode: Mode = Mode.All

    def __init__(self, change_notifier: ChangeNotifier, ui_state: UIState, db_commands: AsyncDbCommands):
        self.ui_state = ui_state
        self.db_commands = db_commands

        change_notifier.register(self, UpdateNodeSearch)

    def handle_change(self, change: Change):
        if isinstance(change, UpdateNodeSearch):
            self._update_search(change.text)
        else:
            assert f'Change not handled: {change}'

    def _update_search(self, text: str):
        asyncio.get_event_loop().create_task(self._update_search_async(text))

    async def _update_search_async(self, text: str):
        if not text:
            self.ui_state.search.matched_nodes = None
        else:
            matching_node_ids = await self.db_commands.enqueue_database_transaction(
                db.get_nodes_matching_text,
                args=[consts.ROOT_NODE_ID, text]
            )

            matching_nodes = []
            for _id in matching_node_ids:
                matching_node = await self.db_commands.enqueue_database_transaction(
                    db.get_node,
                    args=[_id]
                )
                matching_nodes.append(matching_node)

            self.ui_state.search.matched_nodes = matching_nodes
        gls.null_event_required = True
        self.ui_state.selection.ensure_something_selected()
