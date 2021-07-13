
from common_imports import *

from enum import Enum

from .interface import WindowInterface
from .different_window import DifferentWindowScreen
from .same_window import SameWindowScreen


class WindowType(Enum):
    same_process = 'same_process'
    external_process = 'external_process'


class WindowManager:
    _window_manager: WindowInterface

    def __init__(self, window_type: WindowType):
        self.window_type = window_type

    def __enter__(self) -> WindowInterface:
        if self.window_type == WindowType.same_process:
            self._window_manager = SameWindowScreen()
        elif self.window_type == WindowType.external_process:
            self._window_manager = DifferentWindowScreen()
        else:
            raise Exception(f'unhandled type: {self.window_type}')

        self._window_manager.__enter__()
        return self._window_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._window_manager.__exit__(exc_type, exc_val, exc_tb)
