
import pickle
import time

from typing import *

import pywintypes
import win32api
import win32file
import win32pipe


def _serialize(msg: Any) -> bytes:
    return pickle.dumps(msg)


def _deserialize(raw: bytes) -> Any:
    return pickle.loads(raw)


class WindowsPipeAbstract:
    _pipe: Any

    def __init__(self, pipe_name: str, max_buffer_size: int):
        self.pipe_name = pipe_name
        self.max_buffer_size = max_buffer_size

    def __enter__(self):
        self._setup_named_pipe()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def _setup_named_pipe(self):
        ...

    def _cleanup(self):
        ...

    def send_message(self, msg: Any):
        data = pickle.dumps(msg)
        try:
            win32file.WriteFile(self._pipe, data)
        except pywintypes.error as e:
            if e.args[0] == 109:
                raise BrokenPipeError(f'{e}')
            else:
                raise e

    def receive_message(self) -> Any:
        try:
            res = win32pipe.PeekNamedPipe(self._pipe, self.max_buffer_size)
            if res[0]:
                res = win32file.ReadFile(self._pipe, self.max_buffer_size)
                return _deserialize(res[1])
        except pywintypes.error as e:
            if e.args[0] == 109:
                raise BrokenPipeError(f'{e}')
            else:
                raise e

    def any_messages(self) -> bool:
        return len(win32pipe.PeekNamedPipe(self._pipe, self.max_buffer_size)[0]) > 0


class WindowsPipeServer(WindowsPipeAbstract):

    def _setup_named_pipe(self):
        print('Setting up named pipe')
        self._pipe = win32pipe.CreateNamedPipe(
            self.pipe_name,  # pipeName
            win32pipe.PIPE_ACCESS_DUPLEX,  # openMode (duplex allows bidrectional comms)
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,  # pipeMode
            1,  # nMaxInstances
            self.max_buffer_size,  # nOutBufferSize
            self.max_buffer_size,  # nInBufferSize
            0,  # nDefaultT imeOut (defaults to 50ms or something like that)
            None,  # sa (security attributes)
        )

    def _cleanup(self):
        win32file.CloseHandle(self._pipe)

    def await_connection(self):
        print('Waiting for client to connect')
        win32pipe.ConnectNamedPipe(self._pipe, None)  # blocking
        print('Connected to client')


class WindowsPipeClient(WindowsPipeAbstract):
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...

    def _setup_named_pipe(self):

        while True:
            try:
                self._pipe = win32file.CreateFile(
                    self.pipe_name,  # fileName
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,  # desiredAccess
                    0,  # shareMode
                    None,  # attributes
                    win32file.OPEN_EXISTING,  # CreationDisposition
                    0,  # flagsAndAttributes
                    None,  # hTemplateFile
                )
                break
            except pywintypes.error as e:
                if e.args[0] == 2:
                    print('Failed to connect to pipe. Trying again ...')
                    time.sleep(.2)
                    continue

        res = win32pipe.SetNamedPipeHandleState(self._pipe, win32pipe.PIPE_READMODE_MESSAGE, None, None)
        if res == 0:
            last_error = win32api.GetLastError()
            raise Exception(f'Failed to connect to pipe with error: {last_error}')
