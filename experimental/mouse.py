from asciimatics.screen import Screen
from time import sleep
import time

def demo(screen):
    # screen.print_at('Hello world!', 0, 0)
    screen.refresh()
    while True:
        sleep(.1)
        events = []
        while True:
            e = screen.get_event()
            if e is not None:
                events.append(e)
            else:
                break
        clicks = [e for e in events if e.buttons]
        if clicks:
            screen.print_at(f'Click! {clicks[0].buttons}', 0, 0)
            screen.refresh()
        else:
            screen.print_at('                        ', 0, 0)
            screen.refresh()
        pass


Screen.wrapper(demo)
