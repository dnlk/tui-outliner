from typing import *

T = TypeVar("T")
S = TypeVar("S")


class P(Protocol[T]):
    def foo(self) -> T:
        ...

class T_imp:
    pass


class P_imp:
    def foo(self) -> T_imp:
        ...

class Q_imp:
    def foo(self) -> T:
        ...

class X(Generic[T, P]):
    def foo(self, t: T, p: P[T]):
        ...


class Y(X[T_imp, Q_imp]):
    ...


Y().foo(1, 2)
Y().foo(T_imp(), P_imp())
Y().foo(T_imp(), 'a')
Y().foo(T_imp(), T)


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
