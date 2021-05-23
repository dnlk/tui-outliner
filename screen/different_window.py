
from typing import *

import os
import subprocess
import time

from ext.geometry import Coord

import globals as gls

from events.keys import Key, KeyEvent
from screen import different_window_ipc_data as ipc_data
from screen.windows_pipe import WindowsPipeServer
from view.color import Color


class DifferentWindowScreen:
    _child_process: subprocess.Popen

    _CHILD_PROCESS_SCRIPT = os.path.join(os.path.dirname(__file__), 'different_window_child_process.py')

    def __init__(self):
        self.width = 80  # Default - expect it to get overwritten
        self.height = 40    # Default - expect it to get overwritten
        self._pipe = WindowsPipeServer(ipc_data.PIPE_NAME, ipc_data.MAX_BUFFER_SIZE)

    def __enter__(self):
        self._pipe.__enter__()
        self._await_setup_of_window_screen()
        return self

    def _await_setup_of_window_screen(self):
        self._launch_window_client_process()
        self._pipe.await_connection()
        screen_info = self._await_screen_info()
        self.width = screen_info.width
        self.height = screen_info.height

    def _launch_window_client_process(self):
        self._child_process = subprocess.Popen(
            ['cmd', '/c', self._CHILD_PROCESS_SCRIPT],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print('Launched window client')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pipe.__exit__(exc_type, exc_val, exc_tb)
        self._child_process.terminate()

    def _receive_message(self) -> Optional[ipc_data.Message]:
        if msg := self._pipe.receive_message():
            assert isinstance(msg, ipc_data.Message)
            if isinstance(msg, ipc_data.Log):
                print(f'[window child process] {msg.text}')
            else:
                return msg

    def _filter_message_of_type(self, msg_type: Type[ipc_data.Message]):
        msg = self._receive_message()
        if isinstance(msg, msg_type):
            return msg

    def _await_message_of_type(self, msg_type: Type[ipc_data.Message]):
        print(f'Awaiting message of type: {msg_type}')
        while True:
            if msg := self._filter_message_of_type(msg_type):
                print(f'Received awaited message: {msg}')
                return msg
            time.sleep(.05)

    def _await_screen_info(self) -> ipc_data.ScreenInfo:
        msg = self._await_message_of_type(ipc_data.ScreenInfo)
        assert isinstance(msg, ipc_data.ScreenInfo)
        return msg

    def get_next_key(self):
        if gls.null_event_required:
            gls.null_event_required = False
            return KeyEvent(Key.NULL, set(), '')

        if key_event := self._filter_message_of_type(ipc_data.KeyEvent):
            assert isinstance(key_event, ipc_data.KeyEvent)
            return key_event.key

    def _send_message(self, msg: ipc_data.Message):
        assert isinstance(msg, ipc_data.Message)
        self._pipe.send_message(msg)

    def print(self, text, coord: Coord, fg_color: Color, bg_color: Color, attr=0, transparent=False):
        msg = ipc_data.Print(
            text=text,
            coord=coord,
            fg_color=fg_color,
            bg_color=bg_color,
            attr=attr,
            transparent=transparent,
        )
        self._send_message(msg)

    def refresh(self):
        msg = ipc_data.Refresh()
        self._send_message(msg)

    def clear(self):
        msg = ipc_data.Clear()
        self._send_message(msg)
