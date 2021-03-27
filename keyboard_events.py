
import asyncio


class KeyboardEventAsync:
    def __init__(self, keyboard_events_impl):
        self.keyboard_events_impl = keyboard_events_impl

    async def next_key(self):
        while True:
            next_key = self.keyboard_events_impl.get_next_key()
            if next_key is not None:
                return next_key
            else:
                await asyncio.sleep(.01)
