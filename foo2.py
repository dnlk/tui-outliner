from typing import *

T = TypeVar("T")
S = TypeVar("S")


class G(Generic[T]):
    def method(self, t: T):
        pass


class A(Generic[T]):
    G_ = Union[G[T]]

    def method(self, g: G_):
        pass


class B(A[int]):
    pass


class C(A[str]):
    pass


class H(G[int]):
    pass


class I(G[str]):
    pass


B().method(H())
B().method(I())
C().method(H())
C().method(I())
