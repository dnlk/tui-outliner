
import enum


class NodeType(enum.Enum):
    Bullet = 0
    CheckBox = 1


class Mode(enum.Enum):
    All = 0
    Navigate = 1
    EditNode = 2
    Filter = 3


class TreeLink(enum.Enum):
    Parent = 0
    Sibling = 1

    def __str__(self):
        return str(self.value)
