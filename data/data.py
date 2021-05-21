
from typing import *

from asyncio import Queue

from actions.notifier import ChangeAction

T = TypeVar('T')


class DataChangeListener(Protocol[T]):
    def handle_data_change(self, value: 'Data[T]') -> ChangeAction:
        ...


class Data(Generic[T]):
    def __init__(self, change_queue: Queue, value: T):
        self.change_queue = change_queue
        self.value = value
        self._listeners: List[DataChangeListener[T]] = []

    def set_data(self, value: T):
        self.value = value
        self.notify()

    def register_listener(self, data_change_listener: DataChangeListener[T]):
        assert data_change_listener not in self._listeners
        self._listeners.append(data_change_listener)

    def notify(self):
        for listener in self._listeners:
            changes = listener.handle_data_change(self)
            self.change_queue.put_nowait(changes)
