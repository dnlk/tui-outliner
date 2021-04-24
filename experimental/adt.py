
import enum

import containers_ext


Self = "SELF"


def type_match(v, T):
    Ts = T if isinstance(T, tuple) else (T,)

    if v is None and None in Ts:
        return True
    else:
        return any(
            isinstance(v, T) or getattr(v, '_enum_class', None) == T
            for T in Ts
        )


class Data:
    data_types = NotImplemented
    named_data_types = NotImplemented
    _enum_class = NotImplemented
    _enum_instance = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__()

        assert len(args) == 0 or len(kwargs) == 0

        if kwargs:
            assert self.named_data_types.keys() == kwargs.keys(), (self.named_data_types.keys(), kwargs.keys())

            # Set named values
            for k, v in kwargs.items():
                T = self.named_data_types[k]
                assert type_match(v, T), (v, T)
                setattr(self, k, v)

            args = kwargs.values()

        assert len(args) == len(self.data_types)

        # Set unnamed values
        sorted_kwargs_values = []
        for a, T in zip(args, self.data_types):
            assert type_match(a, T)
            sorted_kwargs_values.append(a)

        self.named_values = kwargs
        self.unnamed_values = tuple(sorted_kwargs_values)

    @classmethod
    def set_enum_class(cls, enum_class):
        cls._enum_class = enum_class
        cls.data_types = [enum_class if x == Self else x for x in cls.data_types]
        cls.named_data_types = {k: (enum_class if v == Self else v) for k, v in cls.named_data_types.items()}

    def is_data(self, enum_instance):
        return enum_instance == self._enum_instance

    def is_one_of(self, enum_instances):
        return self._enum_instance in enum_instances

    def __iter__(self):
        return iter(self.unnamed_values)

    def __repr__(self):
        if self.named_values:
            values = ', '.join('{}={}'.format(repr(k), repr(v)) for k, v in self.named_values.items())
        else:
            values = ', '.join(repr(x) for x in self.unnamed_values)
        return '{enum} | {data}({values})'.format(
            enum=self._enum_class.__name__,
            data=self.__class__.__name__,
            values=values
        )

    def __eq__(self, other):
        if not isinstance(other, Data):
            return False
        return self.unnamed_values == other.unnamed_values

    def __hash__(self):
        return hash(self.unnamed_values)


def make_data_class(class_name, data_types):

    if isinstance(data_types, tuple):
        data_types = data_types
        named_data_types = {}
    elif isinstance(data_types, dict):
        named_data_types = data_types
        data_types = tuple(data_types.values())
    else:
        data_types = (data_types,)
        named_data_types = {}

    classdict = {
        'data_types': data_types,
        'named_data_types': named_data_types,
    }

    return type(class_name, (Data,), classdict)


class _Meta(enum.EnumMeta):
    def __new__(cls, name, bases, classdict):
        member_names = classdict._member_names[:]

        data_classes = []

        for i, member_name in reversed(list(enumerate(member_names))):
            data_type = classdict[member_name]
            classdict._member_names.pop(i)
            classdict.pop(member_name)
            data_class = make_data_class(member_name, data_type)
            classdict[member_name] = data_class

            data_classes.append(data_class)

        new_cls = super().__new__(cls, name, bases, classdict)

        new_cls.data_classes = data_classes

        for dc in data_classes:
            for i, dt in enumerate(dc.data_types[:]):
                if dt == Self:
                    new_cls.data_classes = containers_ext.replace_value_at_index(dc.data_types, i, new_cls)

        for t in list(new_cls):
            t.value.set_enum_class(new_cls)
            t.value._enum_instance = t

        return new_cls


class DataEnum(enum.Enum, metaclass=_Meta):
    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)


if __name__ == '__main__':

    class Baz(DataEnum):
        X = int,


    class Foo(DataEnum):
        A = str, int
        B = Baz


    class Bar(DataEnum):
        A = {'x': str, 'y': int}
        B = {'a': bool, 'b': int, 'c': str, 'd': list}


    class List(DataEnum):
        Null = ()
        Cons = int, Self


    class BTree(DataEnum):
        Node = Self, int, Self
        Null = ()


    a = Baz.X(4)
    b = Foo.A("hi", 4)
    c = Foo.B(a)
    d = Bar.A(x="hi", y=3)
    e = List.Cons(1, List.Cons(2, List.Cons(3, List.Null())))
    f = Bar.B(a=True, b=3, c="ok", d=[1,2,3])

    g = BTree.Node(
        BTree.Node(
            BTree.Null(),
            8,
            BTree.Null()
        ),
        5,
        BTree.Node(
            BTree.Null(),
            3,
            BTree.Node(
                BTree.Null(),
                2,
                BTree.Null()
            )
        )
    )

    repr(List.Null)
    x = 0
