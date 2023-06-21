import atexit
import logging
import socket
import json
import time
from dataclasses import dataclass




class BaseClient:
    def __init__(self, timeout: int = 10, buffer: int = 1024):  # timeout in seconds
        self.socket = None  # socket object
        self.address = None  # address of server
        self.timeout = timeout  # timeout in seconds
        self.buffer = buffer  # buffer size in bytes

        self.logger = logging.getLogger("socket_client")

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s:%(name)s - %(message)s"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.ai_name = "test1 AI1"
        self.end = {"cmd": "game_over"}

        atexit.register(self.shutdown)

    def connect(
        self, address, family: int, typ: int, proto: int
    ):  # family: AF_INET, AF_INET6, AF_UNIX; typ: SOCK_STREAM, SOCK_DGRAM, SOCK_RAW
        self.logger.info(f"Connect to {address}")
        self.address = address  # address of server
        self.socket = socket.socket(family, typ, proto)  # create socket object
        self.socket.settimeout(self.timeout)  # set timeout
        self.socket.connect(self.address)  # connect to server
        self.logger.info(f"Connect to {address} success")

    def send(self, message: str = "") -> None:
        flag = False
        while True:
            if message == "":
                message_send = input("> ")
            else:
                message_send = message
                flag = True
            self.socket.send(message_send.encode("utf-8"))
            self.logger.info(f"Send message : {message_send}")
            message_recv = self.socket.recv(self.buffer).decode("utf-8")
            self.logger.info(f"Receive message : {message_recv}")
            if flag:
                break

        # return message_recv

    def receive(self) -> str:
        message = self.socket.recv(self.buffer).decode("utf-8")
        self.logger.info(f"Receive message : {message}")
        s = json.dumps(message)
        return s

    def dc_ok(self) -> None:
        message: dict = {"cmd": "dc_ok", "name": self.ai_name}
        s = json.dumps(message)
        s = s + "\n"
        self.send(s)
    
    def ready(self):
        ready : dict = {
    "cmd": "ready_ok",
    "player_order": [0,1,3,2]}
        s:str = json.dumps(ready)
        s = s + "\n"
        self.send(s)

    def move(self):
        shot : dict = {"cmd": "move","move": {"type": "shot","velocity": { "x": 0.0, "y": 4.0 },"rotation": "ccw"}}  #まっすぐ投げる
        s:str = json.dumps(shot)
        s = s + "\n"
        self.send(s)

    def battle(self, message = "") -> None:
        for i in range(8):
            message = self.receive()
            self.logger.info(f"Receive message : {message}")
            self.move()
            time.sleep(10) #これだと最後に無駄な起動を起こす

    def shutdown(self):
        self.logger.info("Shutdown socket")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.logger.info("Shutdown socket success")
        except BaseException as e:
            self.logger.error(f"Shutdown socket failed {e}")
            pass


class SocketClient1(BaseClient):
    def __init__(self, host: str = "dc3-server", port: int = 10001) -> None:
        self.server = (host, port)
        super().__init__(timeout=60, buffer=1024)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)


if __name__ == "__main__":
    cli = SocketClient1()
    cli.receive()
    cli.dc_ok()
    cli.receive()
    cli.ready()
    a:str = cli.receive()
    self.logger.info(f"Receive message : {a}")

    # print(json.loads(ready))
