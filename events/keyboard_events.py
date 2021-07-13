
from common_imports import *

import asyncio

import globals

from events.keys import Key, KeyEvent


class KeyEventProvider(Protocol):
    def get_next_key(self) -> KeyEvent:
        ...


class KeyboardEventAsync:
    def __init__(self, keyboard_events_impl: KeyEventProvider):
        self.keyboard_events_impl = keyboard_events_impl

    async def next_key(self):
        while True:
            if globals.null_event_required:
                globals.null_event_required = False
                return KeyEvent(Key.NULL, set(), '')
            next_key = self.keyboard_events_impl.get_next_key()
            if next_key is not None:
                return next_key
            else:
                await asyncio.sleep(.01)
