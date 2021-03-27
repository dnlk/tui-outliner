
from typing import Generic, TypeVar, Type, ClassVar, Union, Any, ForwardRef, List, Union
import typing



T = TypeVar('T')
S = TypeVar('S')
# U = TypeVar('U', T)


class C(Generic[T]):
    value: T

    def __init__(self):
        pass

    def __call__(self) -> T:
        pass


class D(Generic[T]):
    t: T

    def __call__(self) -> T:
        pass


Category = C[T]


class B(Category[T]):
    _category = D['B[S]']
    x: 'D[B[int]]'
    y: _category[int]


def accept_str(x: str):
    pass


def accept_int(x: int):
    pass


def accept_list_int(x: List[int]):
    pass


def accept_B(x: B):
    pass


def accept_B_X(x: B.x):
    pass


accept_int(B.x().value)
accept_str(B.x().value)
accept_B(B.x())

accept_int(B.y().value)
accept_str(B.y().value)
accept_B(B.y())


class Categories:
    # def __init__(self, t: T):
    #     self.data = t
    pass

class Category(Generic[T]):

    def __init__(self, t: T):
        self.data = t

    def __call__(self, t: T):
        return Instance[S](t, self)


class C(Categories):
    pass


class MyThings(Categories):
    x: ClassVar[Type[Union[Category[int], 'MyThings']]]
    y: ClassVar[Type[Union[Category[str], 'MyThings']]]


MyThings.x(1)
MyThings.x("hi")



class Instance(Generic[T]):
    def __init__(self, data, category):
        self.data = data
        self.category = category

    def is_category(self, category):
        return self.category is category


class FooMeta(type):

    def __new__(typ, name, bases, classdict):
        new_class = super().__new__(typ, name, bases, classdict)
        for name, type_ in new_class.__dict__.get('__annotations__', {}).items():
            class FooSubClass(new_class):
                pass
                # def __init__(self, t: type_):
                #     self.t = t
            setattr(new_class, name, FooSubClass)

        return new_class


# class Bar(Generic[T]):
#     value: T
#
#     def __init__(self, t: T):
#         self.value = t
#
#
# class Foo:
#     x: ClassVar[Type[Bar[int]]]
#     y: ClassVar[Type[Bar[str]]]



if __name__ == '__main__':

    C = Bar[int]
    D = Bar[str]

    C(4)
    C("hi")
    D(4)
    D("hi")

    a1 = Foo.x("hi")
    a2 = Foo.x(3)
    a3 = Foo.x(2.2)
    b = Foo.y("hi")

    # class A(Categories):
    #     x = Category['A', int]
    #     y = Category['A', float]
    #
    # class B(Categories):
    #     z = Category['B', str]
    #
    #
    # def accepts_A(a: A):
    #     pass
    #
    #
    # def accepts_B(b: B):
    #     pass
    #
    #
    # def accepts_A_x(x: A.x):
    #     pass
    #
    #
    # a_x = A.x(1)
    # a_y = A.y(2.2)
    #
    # accepts_A(a_x)
    # accepts_B(a_x)
    # accepts_A_x(a_x)
    # accepts_A_x(a_y)
    #
    #
    # pass
