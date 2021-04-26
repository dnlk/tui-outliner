
import asyncio

async def f():
    print("Starting")
    x = await asyncio.get_event_loop().create_future()
    print(x)


async def main():
    coro = f()
    fut = next(coro)


asyncio.run(main())