#このファイルは使わない

import asyncio
import websockets

async def hello():
    uri = "ws://localhost:10000"    # 接続するサーバーのURI
    async with websockets.connect(uri) as websocket:    # サーバーに接続する
        data:str = await websocket.recv()   # サーバーからのデータを受信する。
        await websocket.send("dc_ok")   # サーバーにデータを送信する。
        await websocket.send("echo : " + data)  # サーバーにデータを送信する。
   
    print(data)

asyncio.run(hello())    # hello()を実行する。