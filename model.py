import adt
import enums
from typing import Callable, Generic, TypeVar, ClassVar




# class NodeTempId(NodeId):
#     def __init__(self):
#         global __last_temp_id
#         __last_temp_id += 1
#         self.id = __last_temp_id


class Node(adt.DataEnum):
    Bullet = {
        'id': int,
        'parent_id': int,
        'previous_sibling_id': (int, None),
        'next_sibling_id': (int, None),
        'text': str,
        'expanded': bool,
        'child_ids': list
    }


DB_ENUMERATIONS = {
    Node.Bullet: 0
}

DB_ENUMERATIONS_LOOKUP = {v: k for k, v in DB_ENUMERATIONS.items()}
