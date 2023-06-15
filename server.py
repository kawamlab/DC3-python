import asyncio
import websockets

async def echo(websocket, path):
    a ="dc"
    b = "is_ready"
    print(a)
    await websocket.send(a)
    c =await websocket.recv()
    print(c)
    await websocket.send(b)
    print(b)
    d =await websocket.recv()
    print(d)

async def main():
    async with websockets.serve(echo, "localhost", 1000):
        await asyncio.Future()

asyncio.run(main())