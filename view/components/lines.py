

from typing import *

from ..text import Line


class LinesDataProvider(Protocol):
    def set_width(self, width: int):
        ...

    def get_lines(self) -> List[Line]:
        ...

    def num_lines(self) -> int:
        ...


class Lines:
    assigned_y: int
    assigned_height: int

    def __init__(self, lines_data_provider: LinesDataProvider, width: int):
        self.lines_data_provider = lines_data_provider
        self.width = width
        self.lines_data_provider.set_width(self.width)

    def get_height(self) -> int:
        return self.lines_data_provider.num_lines()

    def get_rendered_lines(self) -> List[Line]:
        return self.lines_data_provider.get_lines()
