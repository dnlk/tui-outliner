
from common_imports import *

from ext import func
from datastructures.tree import UniqueNodeLinks


Id = TypeVar('Id')
Item = TypeVar('Item')


T = TypeVar('T', covariant=True)


class IdFactory(Protocol[T]):
    def make_unique_id(self) -> T:
        ...

    def make_invalid_id(self) -> T:
        ...


class DefaultId(int):
    @staticmethod
    def invalid() -> 'DefaultId':
        return DefaultId(-1)

    def is_valid(self) -> bool:
        return self != DefaultId.invalid()

    def __bool__(self):
        return self.is_valid()


class DefaultIdFactory:
    _last_unique_id = -1

    def make_unique_id(self) -> DefaultId:
        self._last_unique_id += 1
        return DefaultId(self._last_unique_id)

    def make_invalid_id(self) -> DefaultId:
        return DefaultId.invalid()


class Items(Dict[Id, Item]):
    def __setitem__(self, key, value):
        assert key not in self
        return super().__setitem__(key, value)


class LinkedList(Generic[Id, Item]):
    _links: UniqueNodeLinks[Id, None]
    _id_factory: Union[IdFactory[Id], DefaultIdFactory]
    items: Items[Id, Item]
    first: Id
    last: Id

    def __init__(self, items: Iterable[Item] = tuple(), *, id_factory: Optional[IdFactory[Id]] = None):
        self._links = UniqueNodeLinks()
        self._id_factory = id_factory or DefaultIdFactory()
        self.first = self._id_factory.make_invalid_id()
        self.last = self._id_factory.make_invalid_id()

        self.items = Items()
        for i in items:
            self.add_to_end(i)

    def add_to_end(self, item: Item) -> Id:
        if not self.first:
            new_id = self._id_factory.make_unique_id()
            self.first = self.last = new_id
            self.items[new_id] = item
        else:
            self.insert_item_after(self.last, item)

        return self.last

    def insert_after(self, new_id: Id, previous_id: Id):
        self._links.insert_after(new_id, previous_id, None, None)
        if previous_id == self.last:
            self.last = new_id

    def insert_item_after(self, previous_id: Id, item: Item):
        new_id = self._id_factory.make_unique_id()
        self.insert_after(new_id, previous_id)
        self.items[new_id] = item

    def get_next(self, _id: Id) -> Optional[Id]:
        return self._links.get_next(_id, None)

    def get_previous(self, _id: Id) -> Optional[Id]:
        if (previous := self._links.get_previous(_id)) is not None:
            return previous[0]

    def get_ordered_ids(self) -> Iterable[Id]:
        return func.lazy_iterate(
            self.get_next,
            lambda _id: _id == self.last or _id is None,
            initial_value=self.first,
            include_last=True
        )

    def get_ordered_nodes(self) -> Iterable[Item]:
        return (self[_id] for _id in self.get_ordered_ids())

    __iter__: Callable[[], Iterable[Id]] = get_ordered_ids

    def iter_values(self):
        return [self[_id] for _id in self]

    def iter_items(self):
        return [(_id, self[_id]) for _id in self]

    def __getitem__(self, item: Id) -> Item:
        return self.items.get(item)

    def __len__(self):
        return len(self.items)
