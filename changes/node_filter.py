
import asyncio

import globals as gls

from .change import Change, ChangeNotifier, UpdateNodeFilter
import consts
from database.async_db_commands import AsyncDbCommands
from database import db
from enums import Mode
from ui.ui import UIState


class NodeFilterChangeHandler:

    mode: Mode = Mode.All

    def __init__(self, change_notifier: ChangeNotifier, ui_state: UIState, db_commands: AsyncDbCommands):
        self.ui_state = ui_state
        self.db_commands = db_commands

        change_notifier.register(self, UpdateNodeFilter)

    def handle_change(self, change: Change):
        if isinstance(change, UpdateNodeFilter):
            self._update_filter(change.text)
        else:
            assert f'Change not handled: {change}'

    def _update_filter(self, text: str):
        asyncio.get_event_loop().create_task(self._update_filter_async(text))

    async def _update_filter_async(self, text: str):
        if not text:
            self.ui_state.filter.matched_node_ids = None
        else:
            matching_node_ids = await self.db_commands.enqueue_database_transaction(
                db.get_nodes_matching_text_including_ancestors,
                args=[consts.ROOT_NODE_ID, text]
            )
            self.ui_state.filter.matched_node_ids = matching_node_ids
        gls.null_event_required = True
        self.ui_state.selection.ensure_something_selected()
