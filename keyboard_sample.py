import keyboard


def callback(e):
    print('a')


keyboard.add_hotkey
keyboard.on_press_key('a', callback, suppress=False)

keyboard.wait()