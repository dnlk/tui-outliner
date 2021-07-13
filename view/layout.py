
from enum import Enum
from common_imports import *

from .text import Line


class Height(Enum):
    Fill = 'fill'


class LayoutComponent(Protocol):
    assigned_y: int
    assigned_height: int

    # def get_children(self) -> List['LayoutComponent']:
    #     ...

    def get_height(self) -> Union[int, Height]:
        ...

    def get_rendered_lines(self) -> List[Line]:
        ...


class Layout:
    components: List[LayoutComponent]
    width: int
    height: int

    def __init__(self, width: int, height: int, components: List[LayoutComponent]):
        self.width = width
        self.height = height
        self.components = components

    def _scan_for_fill(self) -> Optional[int]:
        fill_components = [
            i for i, c in enumerate(self.components)
            if c.get_height() == Height.Fill
        ]

        if len(fill_components) <= 1:
            return fill_components[0]
        else:
            assert False

    def process_layout(self):
        fill_component_index = self._scan_for_fill()
        first_past_end_index = fill_component_index if fill_component_index is not None else len(self.components)

        y = 0
        for c in self.components[:first_past_end_index]:
            c.assigned_y = y
            h = c.get_height()
            assert h >= 0
            c.assigned_height = h
            y += h

        if fill_component_index is not None:
            tail_component_heights = [
                c.get_height()
                for c
                in self.components[first_past_end_index + 1:]
            ]
            tail_height = sum(tail_component_heights)
            fill_component_height = max(self.height - y - tail_height, 0)

            fill_component = self.components[fill_component_index]
            fill_component.assigned_y = y
            fill_component.assigned_height = fill_component_height
            y += fill_component_height

            for c, c_height in zip(self.components[first_past_end_index + 1:], tail_component_heights):
                c.assigned_y = y
                assert c_height >= 0
                c.assigned_height = c_height
                y += c_height

        assert y <= self.height
