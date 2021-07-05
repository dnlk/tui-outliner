
import sys

import curses
from curses import wrapper
import time



from asciimatics.screen import ManagedScreen
from asciimatics.event import KeyboardEvent
#
#
#
#     stdscr = curses.initscr()
#     stdscr.keypad(1)
#
#
#     x = 0
#     ...


class StreamParser:

    def parsech(self, c: int):
        # 27 91 67
        ...


# def get_chrs(stdscr):

extended_input_mode = b'\x1b\x5b>1u'
stop_extended_input_mode = b'\x1b\x5b1<u'
query_flags = b'\x1b\x5b?u'


# print(extended_input_mode)


def main(stdscr):
    # sys.stdout.buffer.write(stop_extended_input_mode)
    # sys.stdout.buffer.write(query_flags)
    # sys.stdout.flush()
    # stdscr.timeout(0)
    # stdscr.keypad(1)
    # curses.noecho()
    # curses.cbreak()
    # curses.raw()

    with ManagedScreen() as screen:
        stdscr = screen._screen

        while True:

            # x = stdscr.getkey()
            chrs = []
            keys = []

            # while x := screen.get_event():
            #     if isinstance(x, KeyboardEvent):
            #         keys.append(x.key_code)


            while (x := stdscr.getch()) != -1:
                chrs.append(x)
            #
            # for x in reversed(chrs):
            #     curses.ungetch(x)
            #
            # while True:
            #     try:
            #         keys.append(stdscr.get_wch())
            #     except:
            #         break



            # x = stdscr.getstr()
            if chrs or keys:
                stdscr.clear()
                stdscr.addstr(1, 1, str(chrs))
                stdscr.addstr(2, 1, str(keys))



            time.sleep(.1)



wrapper(main)