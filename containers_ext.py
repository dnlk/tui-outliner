
from typing import Generic, Dict, Iterable, Optional, Tuple, TypeVar


def _append(container, value):
    return container + type(container)([value])


def replace_value_at_index(container, index, new_value):
    assert index < len(container)
    return _append(container[:index], new_value) + container[index + 1:]


T = TypeVar('T')
S = TypeVar('S')


class BijectiveMap(Generic[T, S]):

    _lmap: Dict[T, S]
    _rmap: Dict[S, T]

    def __init__(self, pairs: Optional[Iterable[Tuple[T, S]]] = None):
        self._lmap = {}
        self._rmap = {}
        if pairs is not None:
            for a, b in pairs:
                self.set_mapping(a, b)

    def set_mapping(self, a, b):
        assert a not in self._lmap, f'First argument must not be in first set: {a}'
        assert b not in self._rmap, f'Second argument must not be in second set: {b}'

        self._lmap[a] = b
        self._rmap[b] = a

    def lget(self, a: T) -> Optional[S]:
        return self._lmap.get(a)

    def rget(self, b: S) -> Optional[T]:
        return self._rmap.get(b)

    def lpop(self, a: T) -> Optional[S]:
        if a in self._lmap:
            b = self._lmap.pop(a)
            if b in self._rmap:
                self._rmap.pop(b)
            return b

    def rpop(self, b: S) -> Optional[T]:
        if b in self._rmap:
            a = self._rmap.pop(b)
            if a in self._lmap:
                self._lmap.pop(a)
            return a
