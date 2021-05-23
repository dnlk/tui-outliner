import time
import sys
import win32pipe, win32file, pywintypes


def pipe_server():
    print("pipe server")
    count = 0
    pipe = win32pipe.CreateNamedPipe(
        r'\\.\pipe\Goo',  # pipeName
        win32pipe.PIPE_ACCESS_DUPLEX,  # openMode
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,  # pipeMode
        1,  # nMaxInstances
        65536,  # nOutBufferSize
        65536,  # nInBufferSize
        0,  # nDefaultTimeOut
        None,  # sa
    )
    try:
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")

        # x = input()

        t0 = time.time()

        while True:
            if time.time() - t0 >= .5:
                t0 = time.time()
                win32file.WriteFile(pipe, f'{time.time()}'.encode('ascii'))
                print('sending')

            time.sleep(.1)

            # res = win32pipe.PeekNamedPipe(pipe, 6666)
            # if res[0]:
            #     win32file.ReadFile(pipe, 6666)

            # res = win32file.ReadFile(pipe, 64*1024)
            # print(res or 'None')




        # while count < 10:
        #     print(f"writing message {count}")
        #     # convert to bytes
        #     some_data = str.encode(f"{count}")
        #     win32file.WriteFile(pipe, some_data)
        #     time.sleep(1)
        #     count += 1

        # print("finished now")
    finally:
        win32file.CloseHandle(pipe)


def pipe_client():
    print("pipe client")
    quit = False

    while not quit:
        try:
            handle = win32file.CreateFile(
                r'\\.\pipe\Goo',
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            print('Opened handle')
            res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            print('Got result')
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")

            while True:
                # win32file.WriteFile(handle, b'abcd')
                time.sleep(.5)
                resp = win32pipe.PeekNamedPipe(handle, 6666)
                # resp = win32file.ReadFile(handle, 64*1024)
                print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True


if __name__ == '__main__':

    import subprocess
    if len(sys.argv) < 2:

        p2 = subprocess.Popen(['cmd', '/c', __file__, 'c'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        pipe_server()
        while True:
            time.sleep(1)
    elif sys.argv[1] == "c":
        pipe_client()

