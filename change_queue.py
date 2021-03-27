
import db

from typing import Callable, List
from change import NodeChange


ObserverType = Callable[[int], str]


class PendingChanges:

    observers: List[ObserverType]

    def __init__(self, conn):
        self.conn = conn
        self.observers = []

    def queue_change(self, change: NodeChange):
        self._apply_change(change)

    def register_observer(self, observer: ObserverType):
        self.observers.append(observer)

    def _apply_change(self, change: NodeChange):
        node = change.node_final
        result = db.update_node(
            self.conn,
            node.id,
            parent_id=node.parent_id,
            previous_sibling_id=node.previous_sibling_id,
            next_sibling_id=node.next_sibling_id,
            type=node.type,
            text=node.text,
            # expanded=node.expanded
        )
        self.notify_observers(change)


    def notify_observers(self, change: NodeChange):
        for observer in self.observers:
            observer(change.pending_change)
