
from dataclasses import dataclass
import enum
from typing import Set


class Key(enum.Enum):
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'
    G = 'g'
    H = 'h'
    I = 'i'
    J = 'j'
    K = 'k'
    L = 'l'
    M = 'm'
    N = 'n'
    O = 'o'
    P = 'p'
    Q = 'q'
    R = 'r'
    S = 's'
    T = 't'
    U = 'u'
    V = 'v'
    W = 'w'
    X = 'x'
    Y = 'y'
    Z = 'z'
    NUM_0 = '0'
    NUM_1 = '1'
    NUM_2 = '2'
    NUM_3 = '3'
    NUM_4 = '4'
    NUM_5 = '5'
    NUM_6 = '6'
    NUM_7 = '7'
    NUM_8 = '8'
    NUM_9 = '9'
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'
    TAB = 'tab'
    ESCAPE = 'escape'
    BACK = 'back'
    DELETE = 'delete'
    SPACE = 'space'
    RETURN = 'return'


class Modifier(enum.Enum):
    Alt = 'alt'
    Control = 'control'
    Shift = 'shift'


Alt = Modifier.Alt
Control = Modifier.Control
Shift = Modifier.Shift

#
# class Modifiers:
#     def __init__(self, alt: bool, control: bool, shift: bool):
#         self.alt = alt
#         self.control = control
#         self.shift = shift
#
#     def __repr__(self):
#         mods = []
#         if self.control:
#             mods.append('Control')
#         if self.alt:
#             mods.append('Alt')
#         if self.shift:
#             mods.append('Shift')
#         mods_str = ', '.join(mods)
#         return f'Modifers({mods_str})'


@dataclass
class KeyEvent:
    key: Key
    modifiers: Set[Modifier]
    char: str

    def __eq__(self, other):
        if isinstance(other, KeyEvent):
            other_key_event = other
        elif isinstance(other, Key):
            other_key_event = KeyEvent(other, set(), '')
        elif len(other) == 2 and isinstance(other[0], Key):
            key = other[0]
            if isinstance(other[1], Modifier):
                modifiers = {other[1]}
            elif isinstance(other[1], set):
                modifiers = other[1]
            else:
                raise ValueError(f'KeyEvent cannot be compared with object: {other}')
            other_key_event = KeyEvent(key, modifiers, '')
        else:
            raise ValueError(f'KeyEvent cannot be compared with object: {other}')

        return self.key == other_key_event.key and self.modifiers == other_key_event.modifiers
