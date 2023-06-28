import atexit
import logging
import socket
import json
import time
from models import (
    ActualMove,
    Coordinate,
    ExtraEndScore,
    ExtraEndThinkingTime,
    GameResult,
    LastMove,
    NewGame,
    NormalDist,
    Players,
    Position,
    Scores,
    Setting,
    Simulator,
    State,
    Stones,
    ThinkingTime,
    ThinkingTimeRemaining,
    Update,
    Velocity,
    Version,
    GameRule,
    IsReady,
    ServerDC,
    Trajectory,
    Start,
    Finish,
    Frame,
)


class BaseClient:
    def __init__(self, timeout: int = 10, buffer: int = 8192):  # timeout in seconds
        self.socket = None  # socket object
        self.address = None  # address of server
        self.timeout = timeout  # timeout in seconds
        self.buffer = buffer  # buffer size in bytes

        self.logger = logging.getLogger("socket_client")

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s:%(name)s - %(message)s")
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

        if self.socket is None:
            self.logger.error("Socket is None")
            raise Exception("Socket is None")

    def send(self, message: str = ""):
        flag = False
        while True:
            if message == "":
                message_send = input("> ")
            else:
                message_send = message
                flag = True

            self.socket.send(message_send.encode("utf-8"))  # type: ignore
            self.logger.info(f"Send message : {message_send}")
            # message_recv:str = self.socket.recv(self.buffer).decode("utf-8")
            # self.logger.info(f"Receive message : {message_recv}")
            if flag:
                break

        # return message_recv

    def receive(self) -> dict:
        message: str = self.socket.recv(self.buffer).decode("utf-8")  # type: ignore
        # self.logger.info(f"Receive message : {message}")
        s = json.dumps(message)
        json_data = json.loads(s)
        dict_data = json.loads(json_data)
        return dict_data

    def shutdown(self):
        self.logger.info("Shutdown socket")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)  # type: ignore
            self.socket.close()  # type: ignore
            self.logger.info("Shutdown socket success")
        except BaseException as e:
            self.logger.error(f"Shutdown socket failed {e}")
            pass


class SocketClient(BaseClient):
    def __init__(self, host: str = "dc3-server", port: int = 10000) -> None:
        self.server = (host, port)
        super().__init__(timeout=60, buffer=65536)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)

    def dc_recv(self) -> None:
        """dcを受信"""
        message_recv = self.receive()

        version = Version(major=message_recv["version"]["major"], minor=message_recv["version"]["minor"])

        self.dc = ServerDC(
            cmd=message_recv["cmd"],
            version=version,
            game_id=message_recv["game_id"],
            date_time=message_recv["date_time"],
        )

    def dc_ok(self) -> None:
        """dc_okを送信"""

        message: dict = {"cmd": "dc_ok", "name": self.ai_name}
        message_str: str = json.dumps(message)
        message_str: str = message_str + "\n"
        self.send(message_str)

    def is_ready_recv(self) -> None:
        """is_readyを受信"""

        message_recv = self.receive()

        thinking_time = ThinkingTime(
            team0=message_recv["game"]["setting"]["thinking_time"]["team0"],
            team1=message_recv["game"]["setting"]["thinking_time"]["team1"],
        )

        extra_end_thinking_time = ExtraEndThinkingTime(
            team0=message_recv["game"]["setting"]["extra_end_thinking_time"]["team0"],
            team1=message_recv["game"]["setting"]["extra_end_thinking_time"]["team1"],
        )

        simulator = Simulator(
            simulator_type=message_recv["game"]["simulator"]["type"],
            seconds_per_frame=message_recv["game"]["simulator"]["seconds_per_frame"],
        )

        team0_players = [
            NormalDist(
                max_speed=data["max_speed"],
                seed=None,
                stddev_angle=data["stddev_angle"],
                stddev_speed=data["stddev_speed"],
                type=data["type"],
            )
            for data in message_recv["game"]["players"]["team0"]
        ]
        team1_players = [
            NormalDist(
                type=data["type"],
                stddev_speed=data["stddev_speed"],
                stddev_angle=data["stddev_angle"],
                max_speed=data["max_speed"],
                seed=None,
            )
            for data in message_recv["game"]["players"]["team1"]
        ]

        players = Players(team0=team0_players, team1=team1_players)

        game_setting = Setting(
            max_end=message_recv["game"]["setting"]["max_end"],
            sheet_width=message_recv["game"]["setting"]["sheet_width"],
            five_rock_rule=message_recv["game"]["setting"]["five_rock_rule"],
            thinking_time=thinking_time,
            extra_end_thinking_time=extra_end_thinking_time,
        )

        game = GameRule(
            rule=message_recv["game"]["rule"],
            setting=game_setting,
            players=players,
            simulator=simulator,
        )

        self.match_setting = IsReady(cmd=message_recv["cmd"], team=message_recv["team"], game=game)
        # self.logger.info(f"match_setting : {self.match_setting}")

    def ready_ok(self, player_order: list = [0, 1, 3, 2]) -> None:
        """ready_okを送信"""

        ready: dict = {"cmd": "ready_ok", "player_order": player_order}
        ready_str: str = json.dumps(ready)
        ready_str: str = ready_str + "\n"
        self.send(ready_str)

    def new_game(self) -> None:
        """new_gameを受信"""

        message_recv = self.receive()
        self.newgame = NewGame(cmd=message_recv["cmd"], name=message_recv["name"])

    def update(self) -> None:
        """updateを受信"""

        message_recv = self.receive()
        self.logger.info(f"Receive message : {message_recv}")
        last_move = message_recv["last_move"]

        team0_stone = []
        team1_stone = []
        start_team0_position = []
        start_team1_position = []
        finish_team0_position = []
        finish_team1_position = []
        frame_data = []
        frame_value = []
        

        if message_recv["state"]["game_result"] is None:
            winner = None
            reason = None
        else:
            winner = message_recv["state"]["game_result"]["winner"]
            reason = message_recv["state"]["game_result"]["reason"]

        game_result = GameResult(
            winner=winner,
            reason=reason,
        )

        game_result = game_result

        extra_end_score = ExtraEndScore(
            team0=message_recv["state"]["extra_end_score"]["team0"],
            team1=message_recv["state"]["extra_end_score"]["team1"],
        )

        scores = Scores(
            team0=message_recv["state"]["scores"]["team0"],
            team1=message_recv["state"]["scores"]["team1"],
        )

        # team0_stone = [
        #     Coordinate(
        #         position=[Position(x=data["x"], y=data["y"])], angle=data["angle"]
        #     )
        #     if data != "None"
        #     else None
        #     for data in message_recv["state"]["stones"]["team0"]
        # ]

        # team1_stone = [
        #     Coordinate(
        #     position=[Position(x=data["x"], y=data["y"])],
        #     angle=data["angle"]
        #     )
        #     if data != "None"
        #     else None
        #     for data in message_recv["state"]["stones"]["team1"]
        # ]

        for data in message_recv["state"]["stones"]["team0"]:
            if data is None:
                team0_stone.append(
                    Coordinate(
                        angle=None, position=[Position(x=None, y=None)]
                    )
                )

            else:
                team0_stone.append(
                    Coordinate(
                        angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                    )
                )

        for data in message_recv["state"]["stones"]["team1"]:
            if data is None:
                team1_stone.append(
                    Coordinate(
                        angle=None, position=[Position(x=None, y=None)]
                    )
                )
            else:
                team1_stone.append(
                    Coordinate(
                        angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                    )
                )

        stones = Stones(
            team0=team0_stone,
            team1=team1_stone,
        )

        thinking_time_remaining = ThinkingTimeRemaining(
            team0=message_recv["state"]["thinking_time_remaining"]["team0"],
            team1=message_recv["state"]["thinking_time_remaining"]["team1"],
        )

        if last_move is None:               #last_moveがNoneの場合
            free_guard_zone_foul=False
            type=None
            rotation=None
            x=None
            y=None
            trajectory=None
            seconds_per_frame=None
        else:                               #last_moveがNoneでない場合
            last_move=message_recv["last_move"]
            actual_move=message_recv["last_move"]["actual_move"]
            free_guard_zone_foul=message_recv["last_move"]["free_guard_zone_foul"]
            type=message_recv["last_move"]["actual_move"]["type"]
            velocity=message_recv["last_move"]["actual_move"]["velocity"]
            rotation=message_recv["last_move"]["actual_move"]["rotation"]
            x=message_recv["last_move"]["actual_move"]["velocity"]["x"]
            y=message_recv["last_move"]["actual_move"]["velocity"]["y"]
            if message_recv["last_move"]["trajectory"] is None:                 #trajectoryがNoneの場合
                seconds_per_frame=None
                # x=None
                # y=None
                # if trajectory["start"] is None:
                for data in message_recv["last_move"]["trajectory"]["start"]["team0"]:
                    start_team0_position.append(
                        Coordinate(
                           angle=None, position=[Position(x=None, y=None)]
                        ))
                for data in message_recv["last_move"]["trajectory"]["start"]["team1"]:
                    start_team1_position.append(
                        Coordinate(
                           angle=None, position=[Position(x=None, y=None)]
                        )
                    )
                # if trajectory["finish"] is None:
                for data in message_recv["last_move"]["trajectory"]["finish"]["team0"]:
                    finish_team0_position.append(
                        Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                        )
                    )
                for data in message_recv["last_move"]["trajectory"]["finish"]["team1"]:
                    finish_team1_position.append(
                        Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                        )
                    )

                frame_value.append(
                    Coordinate(
                    angle=None, position=[Position(x=None,y=None)]
                    )
                )

                # if trajectory["frames"] is None:
                frame_data.append(
                    Frame(
                    team=None,
                    index=None,
                    value=frame_value,
                    )
                )

            else:                                            #trajectoryがNoneでない場合
                seconds_per_frame=message_recv["last_move"]["trajectory"]["seconds_per_frame"]
                for data in message_recv["last_move"]["trajectory"]["start"]["team0"]:
                    if data is None:
                        start_team0_position.append(
                            Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                            )
                        )
                    else:
                        start_team0_position.append(
                            Coordinate(
                            angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                            ))
                for data in message_recv["last_move"]["trajectory"]["start"]["team1"]:
                    if data is None:
                        start_team1_position.append(
                            Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                            )
                        )
                    else:
                        start_team1_position.append(
                            Coordinate(
                            angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                            )
                        )
                for data in message_recv["last_move"]["trajectory"]["finish"]["team0"]:
                    if data is None:
                        finish_team0_position.append(
                            Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                            )
                        )
                    else:
                        finish_team0_position.append(
                            Coordinate(
                                angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                            )
                        )
                for data in message_recv["last_move"]["trajectory"]["finish"]["team1"]:
                    if data is None:
                        finish_team1_position.append(
                            Coordinate(
                            angle=None, position=[Position(x=None, y=None)]
                            )
                        )
                    else:
                        finish_team1_position.append(
                            Coordinate(
                                angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                            )
                        )
                for data in message_recv["last_move"]["trajectory"]["frames"]:
                    frame_value.append(
                        Coordinate(
                            angle=data["frames"]["angle"], position=[Position(x=data["frames"]["position"]["x"], y=data["frames"]["position"]["y"])]
                        )
                    )


                for data in message_recv["last_move"]["trajectory"]["frames"]:
                    frame_data.append(
                        Frame(
                        team=data["team"],
                        index=data["index"],
                        value=frame_value,
                        )
                    )


        velocity = Velocity(x=x, y=y)

        actual_move = ActualMove(
            rotation=rotation,
            type=type,
            velocity=velocity,
        )


        start = Start(
            team0=start_team0_position,
            team1=start_team1_position,
        )

        finish = Finish(
            team0=finish_team0_position,
            team1=finish_team1_position,
        )


        trajectory = Trajectory(
            seconds_per_frame = seconds_per_frame,
            start = start,
            finish = finish,
            frames = frame_data,
        )

        last_move = LastMove(
            actual_move=actual_move,
            free_guard_zone_foul=free_guard_zone_foul,
            trajectory=trajectory,
        )

        state = State(
            end=message_recv["state"]["end"],
            extra_end_score=extra_end_score,
            game_result=game_result,
            hammer=message_recv["state"]["hammer"],
            scores=scores,
            shot=message_recv["state"]["shot"],
            stones=stones,
            thinking_time_remaining=thinking_time_remaining,
        )

        self.update_info = Update(
            cmd=message_recv["cmd"],
            last_move=last_move,
            next_team=message_recv["next_team"],
            state=state,
        )

        self.logger.info(f"next_team : {self.update_info.next_team}")

    def move(self):
        time.sleep(3)
        shot: dict = {
            "cmd": "move",
            "move": {
                "type": "shot",
                "velocity": {"x": 0.0, "y": 2.4},
                "rotation": "ccw",
            },
        }  # まっすぐ投げる
        s: str = json.dumps(shot)
        s: str = s + "\n"
        time.sleep(3)
        self.send(s)

    def battle(self) -> None:
        for i in range(8):
            self.move()
            message = self.receive()
            # self.logger.info(f"Receive message : {message}")
