
import aiosqlite
import asyncio
from collections import deque
from common_imports import *


class DatabaseCommand:
    def __init__(self, future: asyncio.Future, coroutine, args, kwargs):
        self.future = future
        self.coroutine = coroutine
        self.args = args
        self.kwargs = kwargs


class DatabaseQueue:
    queue: Deque[DatabaseCommand]

    def __init__(self):
        self.queue = deque()

    def add(self, command: DatabaseCommand):
        self.queue.append(command)

    def pop(self) -> Optional[DatabaseCommand]:
        if len(self.queue) > 0:
            return self.queue.popleft()


async def _process_database_queue(db_path: str, database_queue: DatabaseQueue):
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.cursor()
        while True:
            if next_command := database_queue.pop():
                args = next_command.args or []
                kwargs = next_command.kwargs or {}
                try:
                    command_result = await next_command.coroutine(cursor, *args, **kwargs)
                except Exception as e:
                    exit(69)
                await conn.commit()
                next_command.future.set_result(command_result)
                continue
            else:
                await asyncio.sleep(.01)


class AsyncDbCommands:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.queue = DatabaseQueue()

    def process_database_queue(self):
        asyncio.create_task(_process_database_queue(self.db_path, self.queue))

    def enqueue_database_transaction(self, db_command_coro, args=None, kwargs=None) -> asyncio.Future:
        fut = asyncio.get_running_loop().create_future()
        command = DatabaseCommand(
            future=fut,
            coroutine=db_command_coro,
            args=args,
            kwargs=kwargs
        )
        self.queue.add(command)
        return fut
