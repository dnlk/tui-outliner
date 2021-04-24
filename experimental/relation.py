
from typing import Generic, Tuple, TypeVar, Dict


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Relation(Generic[A]):

    def __init__(
            self,
            unique_constraints,
            indexes,
    ):
        self.unique_constraints = unique_constraints
        self.indexes = indexes
        self.relations: Dict[int, A] = {}
        self.next_row_id = 0

    def add_relation(self, relation: A):
        row_id = self.next_row_id
        self.next_row_id += 1
