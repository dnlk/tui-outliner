
import time

from events.windows_keyboard_events import WindowsKeyEventReader
import screen.different_window_ipc_data as ipc_data
from screen.same_window import SameWindowScreen
from screen.windows_pipe import WindowsPipeClient


def run_pipe_client():
    try:
        with PipeClient() as client:
            print('hi')
            client.run_forever()
    except Exception as e:
        import traceback
        traceback.print_exc()

        # Idly loop so that the terminal stays open, so the stack trace can be seen
        while True:
            time.sleep(.5)


class PipeClient:
    screen: SameWindowScreen
    pipe: WindowsPipeClient

    def __init__(self):
        self.key_event_reader = WindowsKeyEventReader()
        self.pipe = WindowsPipeClient(ipc_data.PIPE_NAME, ipc_data.MAX_BUFFER_SIZE)
        self.screen = SameWindowScreen()

    def __enter__(self):
        print('Connecting to pipe')
        self.pipe.__enter__()
        self.log('Connected to pipe server')
        self.log('Initializing screen')
        self.screen.__enter__()
        self.send_screen_info()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.screen.__exit__(exc_type, exc_val, exc_tb)
        self.pipe.__exit__(exc_type, exc_val, exc_tb)

    def run_forever(self):
        self.log('Running forever')
        while True:
            try:
                self.process_messages()
                self.dispatch_key_events()
                time.sleep(.01)
            except BrokenPipeError:
                print('Broken pipe - finishing up in 2 seconds')
                time.sleep(2)
                return

    def _process_message(self, msg: ipc_data.Message):
        if isinstance(msg, ipc_data.Print):
            self.screen.print(
                text=msg.text,
                coord=msg.coord,
                fg_color=msg.fg_color,
                bg_color=msg.bg_color,
                attr=msg.attr,
                transparent=msg.transparent,
            )
        elif isinstance(msg, ipc_data.Refresh):
            self.screen.refresh()
        elif isinstance(msg, ipc_data.Clear):
            self.screen.clear()
        else:
            raise Exception(f'Unhandled message: {msg}')

    def process_messages(self):
        while self.pipe.any_messages():
            msg = self.pipe.receive_message()
            assert msg
            self._process_message(msg)

    def dispatch_key_events(self):
        while next_key := self.key_event_reader.get_next_key():
            msg = ipc_data.KeyEvent(next_key)
            self.pipe.send_message(msg)

    def log(self, text: str):
        msg = ipc_data.Log(text)
        self.pipe.send_message(msg)

    def send_screen_info(self):
        self.log('Sending screen info')
        screen_info = ipc_data.ScreenInfo(width=self.screen.width, height=self.screen.height)
        self.pipe.send_message(screen_info)


if __name__ == '__main__':
    run_pipe_client()
