import asyncio
import websockets

# async def echo(websocket, path):
#     async for message in websocket:
#         await websocket.send(message)

# async def main():
#     async with websockets.serve(echo, "localhost", 10000):
#         await asyncio.Future()

# asyncio.run(main())

# クライアント接続すると呼び出す。	
async def accept(websocket, path):
  # 無限ループ
  await websockets.send("dc")
  while True:	
    # クライアントからメッセージを待機する。
    data:str = await websocket.recv()	
    # コンソールに出力
    print("receive : " + data)
    # クライアントでechoを付けて再送信する。
    await websocket.send("echo : " + data)
# WebSocketサーバー生成。ホストはlocalhost、portは10000に生成する。

	
start_server = websockets.serve(accept, "localhost", 10000) # 接続を待ち受ける
asyncio.get_event_loop().run_until_complete(start_server) # イベントループを開始

	
asyncio.get_event_loop().run_forever()  # イベントループを開始