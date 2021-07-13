
from common_imports import *


T = TypeVar('T')


class Bindable(Protocol[T]):
    def set_data(self, t: T):
        ...


class Binding(Generic[T]):
    def __init__(self, obj, f: Callable[[], T]):
        self.obj = obj
        self.f = f
        self.other: Optional[Bindable[T]] = None

    def bind(self, other: Optional[Bindable[T]]):
        self.other = other
        return self.obj

    def get(self) -> T:
        return self.f()

    def notify(self):
        if self.other is not None:
            self.other.set_data(self.get())
