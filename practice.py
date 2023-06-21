import atexit
import logging
import socket
import json
import time
from dataclasses import dataclass, asdict

@dataclass
class position():
    x : float
    y : float

@dataclass
class shot():
    rotation : str
    type : str
    velocity : position

@dataclass
class actualmove():
    actual_move : shot

@dataclass
class extraendscore():
    team0 : list
    team1 : list

@dataclass
class play_state():
    end : int
    extra_end_score : extraendscore

@dataclass
class stone():
    team0 : list
    team1 : list

@dataclass
class thinkingtimeremaining():
    team0 : float
    team1 : float

@dataclass
class thinkingtime():
    team0 : float
    team1 : float

@dataclass
class extraendthinkingtime():
    team0 : float
    team1 : float

@dataclass
class simu():
    type : str
    seconds_per_frame : float

@dataclass
class playerconfig():
    team0 : list
    team1 : list

@dataclass
class gamesetting():
    max_end : int
    sheet_width : float
    five_rock_rule : bool
    thinking_time : thinkingtime
    extra_end_thinking_time : extraendthinkingtime

@dataclass
class gamerule():
    rule : str
    setting : gamesetting
    simulater : simu
    players : playerconfig

@dataclass
class update_recv():
    """対戦中の情報を受け取る"""
    cmd : str
    last_move : actualmove
    free_guard_zone_foul : bool
    next_team : str
    state : play_state
    shot : int
    stones : stone
    thinking_time_remaining : thinkingtimeremaining

@dataclass
class isready():
    """対戦開始の際の情報を受け取る(is_ready))"""
    cmd : str
    team : str
    game : gamerule


class BaseClient:
    def __init__(self, timeout: int = 10, buffer: int = 4096):  # timeout in seconds
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

        self.ai_name = "test AI0"
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

    def send(self, message: str = ""):
        flag = False
        while True:
            if message == "":
                message_send = input("> ")
            else:
                message_send = message
                flag = True
            self.socket.send(message_send.encode("utf-8"))
            self.logger.info(f"Send message : {message_send}")
            message_recv:str = self.socket.recv(self.buffer).decode("utf-8")
            self.logger.info(f"Receive message : {message_recv}")
            if flag:
                break

        # return message_recv

    def receive(self) -> str:
        message:str = self.socket.recv(self.buffer).decode("utf-8")
        self.logger.info(f"Receive message : {message}")
        s:str = json.dumps(message)
        return s 

    def dc_ok(self) -> None:
        message: dict = {"cmd": "dc_ok", "name": self.ai_name}
        s:str = json.dumps(message)
        s:str = s + "\n"
        self.send(s)
    
    def ready(self) -> None:
        ready : dict = {
    "cmd": "ready_ok",
    "player_order": [0,1,3,2]}
        s:str = json.dumps(ready)
        s:str = s + "\n"
        self.send(s)

    def move(self):
        shot : dict = {"cmd": "move","move": {"type": "shot","velocity": { "x": 0.0, "y": 2.4},"rotation": "ccw"}}  #まっすぐ投げる
        s:str = json.dumps(shot)
        s:str = s + "\n"
        self.send(s)


    def shutdown(self):
        self.logger.info("Shutdown socket")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.logger.info("Shutdown socket success")
        except BaseException as e:
            self.logger.error(f"Shutdown socket failed {e}")
            pass

    def battle(self) -> None:
        for i in range(8):
            self.move()
            message = self.receive()
            # s = self.update_recv.from_json(message)
            self.logger.info(f"Receive message : {message}")
            time.sleep(10) #これだと最後に無駄な起動を起こす



class SocketClient(BaseClient):
    def __init__(self, host: str = "dc3-server", port: int = 10000) -> None:
        self.server = (host, port)
        super().__init__(timeout=60, buffer=1024)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)


if __name__ == "__main__":
    cli = SocketClient()
    a = cli.receive()
    cli.dc_ok()
    b = cli.receive()
    print(b)
    cli.ready()
    c = cli.receive()
    print(c)
    # print(json.loads(ready))
