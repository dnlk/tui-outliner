
from typing import *

T = TypeVar('T')


class SelectableItem(Generic[T]):
    id: T
    text: str

    def __init__(self, _id: T, text: str):
        self.id = _id
        self.text = text


class SelectableListModel(Generic[T]):
    items: Optional[List[SelectableItem[T]]]
    selected_item: Optional[T]

    def __init__(self):
        self.items = None
        self.selected_item = None

    def _is_item_present(self, _id: T):
        return self._index(_id) != -1

    def _index(self, _id: T):
        for i, item in enumerate(self.get_items()):
            if _id == item.id:
                return i
        return -1

    def _select_first(self):
        if new_item := self.get_first_item():
            self.selected_item = new_item

    def get_selected_item(self) -> Optional[T]:
        return self.selected_item

    def get_first_item(self):
        items = self.get_items()
        if len(items) == 0:
            return
        return items[0].id

    def is_selected(self, item: SelectableItem[T]) -> bool:
        return item.id == self.selected_item

    def _get_item_offset(self, item_id: T, offset: int) -> Optional[SelectableItem[T]]:
        items = self.get_items()
        if not items:
            return None
        if (index := self._index(item_id)) != -1:
            new_index = min(max(0, index + offset), len(items) - 1)
            return items[new_index]
        return None

    def get_next_item(self):
        return self._get_item_offset(self.selected_item, 1)

    def get_previous_item(self):
        return self._get_item_offset(self.selected_item, -1)

    def get_items(self):
        return [] if self.items is None else self.items

    def set_items(self, items):
        if not items:
            self.items = None
            self.selected_item = None
            return

        self.items = items
        if not self._is_item_present(self.selected_item):
            self._select_first()
