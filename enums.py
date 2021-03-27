
import enum


class NodeType(enum.Enum):
    Bullet = 0
    CheckBox = 1


class Mode(enum.Enum):
    Navigate = 0
    EditNode = 1


class TreeLink(enum.Enum):
    Parent = 0
    Sibling = 1

