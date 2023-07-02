import atexit
import json
import logging
import socket
import time
from dataclasses import fields, is_dataclass

from models import (
    ActualMove,
    Coordinate,
    ExtraEndScore,
    ExtraEndThinkingTime,
    Finish,
    Frame,
    GameResult,
    GameRule,
    IsReady,
    LastMove,
    MatchData,
    NewGame,
    NormalDist,
    NormalDist1,
    Players,
    Position,
    Scores,
    ServerDC,
    Setting,
    Simulator,
    Start,
    State,
    Stones,
    ThinkingTime,
    ThinkingTimeRemaining,
    Trajectory,
    Update,
    Velocity,
    Version,
)


class BaseClient:
    def __init__(self, timeout: int = 10, buffer: int = 1024, log_level: int = logging.INFO):
        self.socket = None  # socket object
        self.address = None  # address of server
        self.timeout = timeout  # timeout in seconds
        self.buffer = buffer  # buffer size in bytes

        self.logger = logging.getLogger("socket_client")

        self.logger.setLevel(log_level)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s:%(name)s - %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # AIの名前
        self.ai_name = "test AI0"

        # rate limitのために現在時刻を取得
        self.last_send = time.time()

        # rate limitのしきい値
        self.rate_limit = 3

        # 終了時にソケットを閉じる
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
        if message == "":
            self.logger.info("In Manual Mode")
            while True:
                message = input("> ")
                self.socket.send(message.encode("utf-8"))  # type: ignore
                self.logger.info(f"Send message : {message}")

        else:
            while True:
                if (wait_time := ((now := time.time()) - self.last_send)) > self.rate_limit:
                    self.socket.send(message.encode("utf-8"))  # type: ignore
                    self.logger.info(f"Send message : {message}")
                    self.last_send = now
                    break
                else:
                    self.logger.debug(f"Rate limit {self.rate_limit} seconds")
                    self.logger.debug(f"Please wait {wait_time + .5} seconds")
                    time.sleep(wait_time + 0.5)
            # message_recv:str = self.socket.recv(self.buffer).decode("utf-8")
            # self.logger.info(f"Receive message : {message_recv}")

    def receive(self) -> dict:
        # messageの末尾に改行が現れるまで受信を続ける
        message = ""
        while True:
            message_recv: str = self.socket.recv(self.buffer).decode("utf-8")  # type: ignore
            message += message_recv
            if message_recv[-1] == "\n":
                break

        # self.logger.info(f"Receive message : {message}")
        s = json.dumps(message)
        json_data = json.loads(s)
        dict_data = json.loads(json_data)
        # self.logger.info(f"Receive message : {dict_data}")
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
        super().__init__(timeout=60, buffer=1024)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)

        self.obj_dict = {}

        self.match_data = MatchData()

        self.dc_recv()
        self.dc_ok()  # dc_okを送信
        self.is_ready_recv()  # is_readyを読み取るための受信
        self.ready_ok()  # ready_okを送信
        self.get_new_game()

    def _stone_trajectory_parser(self, message_recv: list) -> list:
        """ストーンの軌跡をデータクラスに変換する

        Args:
            message_recv (list): ストーンの座標データのリスト

        Returns:
            list: ストーンの座標データのデータクラスのリスト
        """
        team_stone: list = []
        for data in message_recv:
            if data is None:
                team_stone.append(Coordinate(angle=None, position=[Position(x=None, y=None)]))

            else:
                team_stone.append(
                    Coordinate(
                        angle=data["angle"], position=[Position(x=data["position"]["x"], y=data["position"]["y"])]
                    )
                )

        return team_stone

    def dc_recv(self):
        """dcを受信"""
        message_recv = self.receive()

        version = Version(major=message_recv["version"]["major"], minor=message_recv["version"]["minor"])

        dc = ServerDC(
            game_id=message_recv["game_id"],
            cmd=message_recv["cmd"],
            version=version,
            date_time=message_recv["date_time"],
        )

        self.match_data.server_dc = dc

    def dc_ok(self) -> None:
        """dc_okを送信"""

        message: dict = {"cmd": "dc_ok", "name": self.ai_name}
        message_str: str = json.dumps(message)
        message_str: str = message_str + "\n"
        self.send(message_str)

    def is_ready_recv(self):
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
                randomness=data["type"],
            )
            for data in message_recv["game"]["players"]["team0"]
        ]

        team1_players = [
            NormalDist1(
                randomness=data["type"],
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

        is_ready = IsReady(cmd=message_recv["cmd"], team=message_recv["team"], game=game)

        self.match_data.is_ready = is_ready

    def ready_ok(self, player_order: list = [0, 1, 3, 2]) -> None:
        """ready_okを送信"""

        ready: dict = {"cmd": "ready_ok", "player_order": player_order}
        ready_str: str = json.dumps(ready)
        ready_str: str = ready_str + "\n"
        self.send(ready_str)

    def get_new_game(self):
        """new_gameを受信"""

        message_recv = self.receive()
        self.match_data.new_game = NewGame(cmd=message_recv["cmd"], name=message_recv["name"])

    def update(self):
        """updateを受信"""

        message_recv = self.receive()
        # self.logger.info(f"Receive message : {message_recv}")

        start_team0_position = []
        start_team1_position = []
        finish_team0_position = []
        finish_team1_position = []
        frame_data = []

        last_move = None
        trajectory = None

        if message_recv["cmd"] != "update":
            return

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

        extra_end_score = ExtraEndScore(
            team0=message_recv["state"]["extra_end_score"]["team0"],
            team1=message_recv["state"]["extra_end_score"]["team1"],
        )

        scores = Scores(
            team0=message_recv["state"]["scores"]["team0"],
            team1=message_recv["state"]["scores"]["team1"],
        )

        stones = Stones(
            team0=self._stone_trajectory_parser(message_recv["state"]["stones"]["team0"]),
            team1=self._stone_trajectory_parser(message_recv["state"]["stones"]["team1"]),
        )

        thinking_time_remaining = ThinkingTimeRemaining(
            team0=message_recv["state"]["thinking_time_remaining"]["team0"],
            team1=message_recv["state"]["thinking_time_remaining"]["team1"],
        )

        if message_recv["last_move"] is None:  # last_moveがNoneの場合
            free_guard_zone_foul = False
            type = None
            rotation = None
            x = None
            y = None
            seconds_per_frame = None
        else:  # last_moveがNoneでない場合
            last_move = message_recv["last_move"]
            actual_move = message_recv["last_move"]["actual_move"]
            free_guard_zone_foul = message_recv["last_move"]["free_guard_zone_foul"]
            type = message_recv["last_move"]["actual_move"]["type"]
            velocity = message_recv["last_move"]["actual_move"]["velocity"]
            rotation = message_recv["last_move"]["actual_move"]["rotation"]
            x = message_recv["last_move"]["actual_move"]["velocity"]["x"]
            y = message_recv["last_move"]["actual_move"]["velocity"]["y"]

            if message_recv["last_move"]["trajectory"] is None:  # trajectoryがNoneの場合
                seconds_per_frame = None

            else:  # trajectoryがNoneでない場合
                seconds_per_frame = message_recv["last_move"]["trajectory"]["seconds_per_frame"]

                start_team0_position = self._stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["start"]["team0"]
                )

                start_team1_position = self._stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["start"]["team1"]
                )

                finish_team0_position = self._stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["finish"]["team0"]
                )

                finish_team1_position = self._stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["finish"]["team1"]
                )

                for frames in message_recv["last_move"]["trajectory"]["frames"]:
                    for frame in frames:
                        if frame is None or frame["value"] is None:
                            frame_data.append(
                                Frame(
                                    team=None,
                                    index=None,
                                    value=Coordinate(angle=None, position=[Position(x=None, y=None)]),
                                )
                            )
                        else:
                            frame_data.append(
                                Frame(
                                    team=frame["team"],
                                    index=frame["index"],
                                    value=Coordinate(
                                        angle=frame["value"]["angle"],
                                        position=[
                                            Position(
                                                x=frame["value"]["position"]["x"], y=frame["value"]["position"]["y"]
                                            )
                                        ],
                                    ),
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
                seconds_per_frame=seconds_per_frame,
                start=start,
                finish=finish,
                frames=frame_data,
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

        update_info = Update(
            cmd=message_recv["cmd"],
            last_move=last_move,
            next_team=message_recv["next_team"],
            state=state,
        )

        self.logger.info(f"next_team : {update_info.next_team}")

        self.match_data.update_list.append(update_info)

    def move(self, x: float = 0.0, y: float = 2.4, rotation: str = "ccw") -> None:
        """ショットを行う

        Args:
            x (float, optional): x軸方向の速度. Defaults to 0.0.
            y (float, optional): y軸方向の速度. Defaults to 2.4.
            rotation (str, optional): 回転方向. Defaults to "ccw".
        """

        shot = {
            "cmd": "move",
            "move": {
                "type": "shot",
                "velocity": {"x": x, "y": y},
                "rotation": rotation,
            },
        }  # まっすぐ投げる
        s: str = json.dumps(shot)
        s: str = s + "\n"
        self.send(s)

    def battle(self) -> None:
        for i in range(8):
            self.move()
            message = self.receive()
            # self.logger.info(f"Receive message : {message}")

    def update_to_json(self, obj):
        if isinstance(obj, list):
            for data in obj:
                # dictに変換
                for field in fields(data):
                    value = getattr(data, field.name)
                    if value is None:
                        self.obj_dict[field.name] = None

                    if is_dataclass(value):
                        self.obj_dict[field.name] = self.update_to_json(value)

                    else:
                        self.obj_dict[field.name] = value
        # for field in fields(obj):
        #     value = getattr(obj, field.name)
        #     # if value is None:
        #     #     obj_dict[field.name] = None

        #     if is_dataclass(value):
        #         self.obj_dict[field.name] = self.update_to_json(value)
        #     elif isinstance(value, list):
        #         self.obj_dict[field.name] = [self.update_to_json(v) for v in value]
        #     elif isinstance(value, dict):
        #         self.obj_dict[field.name] = {k: self.update_to_json(v) for k, v in value.items()}
        #     elif isinstance(value, tuple):
        #         self.obj_dict[field.name] = tuple(self.update_to_json(v) for v in value)
        #     else:
        #         update: str | int | float = value
        #         self.obj_dict[field.name] = update

        return self.obj_dict

    def trajectory_to_json(self, obj: list) -> list:
        """trajectoryをjsonに変換"""
        shot_list = []
        # shotごとのtrajectoryをjsonに変換
        for shot in obj:
            pass
        return shot_list

    def get_my_team(self) -> str:
        """自分のチーム名を返す

        Returns:
            str: 自分のチーム名
        """
        if self.match_data.is_ready is None:
            return "none"

        return self.match_data.is_ready.team

    def get_next_team(self) -> str:
        """次のチーム名を返す"""
        return self.match_data.update_list[-1].next_team

    def get_match_data(self) -> MatchData:
        return self.match_data

    def get_winner(self) -> str | None:
        if self.match_data.update_list[-1].state.game_result is None:
            return "none"

        return self.match_data.update_list[-1].state.game_result.winner

    def get_update_and_trajectory(self, remove_trajectory: bool = True) -> tuple[list[Update], list[Trajectory]]:
        # update_list = self.match_data.update_list
        update_list: list[Update] = []
        trajectory_list: list[Trajectory] = []

        for update_data in self.match_data.update_list:
            if update_data.last_move is not None and update_data.last_move.trajectory is not None:
                trajectory_list.append(update_data.last_move.trajectory)

            if remove_trajectory is True:
                data = update_data  # 元データは変更しないようにする
                if data.last_move is not None:
                    data.last_move.trajectory = None
                update_list.append(data)
            else:
                update_list.append(update_data)

        return update_list, trajectory_list
