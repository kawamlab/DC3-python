import atexit
import json
import logging
import socket
import time
from dataclasses import fields
from typing import Any

from dc3client.models import (
    ActualMove,
    Coordinate,
    DCNotFoundError,
    ExtraEndScore,
    ExtraEndThinkingTime,
    Finish,
    Frame,
    GameResult,
    GameResultNotFoundError,
    GameRule,
    IsReady,
    IsReadyNotFoundError,
    LastMove,
    MatchData,
    NewGame,
    PlayerInfo,
    Players,
    Position,
    Scores,
    ServerDC,
    Setting,
    ShotInfo,
    Simulator,
    Start,
    State,
    StoneRotation,
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
        """base client initialize

        Args:
            timeout (int, optional): Time to client timeout. Defaults to 10.
            buffer (int, optional): Buffer size. Defaults to 1024.
            log_level (int, optional): Minimum level of logging. Defaults to logging.INFO.
        """

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

        # Get current time for rate limit
        self.last_send = time.time()

        # Rate limit time interval
        self.rate_limit = 3.0

    def __connect(self, address: tuple, family: int, typ: int, proto: int):
        self.logger.info(f"Connect to {address}")
        self.address = address  # address of server
        self.socket = socket.socket(family, typ, proto)  # create socket object
        self.socket.settimeout(self.timeout)  # set timeout
        self.socket.connect(self.address)  # connect to server
        self.logger.info(f"Connect to {address} success")

        if self.socket is None:
            self.logger.error("Socket is None")
            raise Exception("Socket is None")
        # Close socket on exit
        atexit.register(self.__shutdown)

    def __send(self, message: str = ""):
        """send message to server

        Args:
            message (str, optional): massage content. Defaults to "".
        """

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

    def __receive(self) -> dict[str, Any]:
        """receive message from server until "\n"

        Returns:
            dict[str, Any]: received message
        """

        message = ""
        while True:
            message_recv: str = self.socket.recv(self.buffer).decode("utf-8")  # type: ignore
            message += message_recv
            if message_recv[-1] == "\n":
                break

        s = json.dumps(message)
        json_data = json.loads(s)
        dict_data = json.loads(json_data)
        return dict_data

    def __shutdown(self):
        """shutdown socket"""
        self.logger.info("Shutdown socket")
        try:
            self.socket.shutdown(socket.SHUT_RDWR)  # type: ignore
            self.socket.close()  # type: ignore
            self.logger.info("Shutdown socket success")
        except BaseException as e:
            self.logger.error(f"Shutdown socket failed {e}")
            pass


class SocketClient(BaseClient):
    def __init__(
        self,
        host: str = "dc3-server",
        port: int = 10000,
        client_name: str = "AI0",
        auto_start: bool = True,
        rate_limit: float = 3.0,
    ) -> None:
        """initialize socket client

        Args:
            host (str, optional): URL of the server of Digital Curling 3. Defaults to "dc3-server".
            port (int, optional): Connection port to Digital Curling Server. Defaults to 10000.
            client_name (str, optional): Identification name of the client. Defaults to "AI0".
            rate_limit (int, optional): Minimum time interval to send data to the server. Defaults to 3.
        """
        self.is_connected = False
        self.server = (host, port)
        super().__init__(timeout=60, buffer=1024)

        self.obj_dict = {}
        self.match_data = MatchData()

        self.move_info: list[ShotInfo] = []

        # Name of the client
        self.client_name = client_name

        if auto_start:
            self.rate_limit = rate_limit
            super().__connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)
            self.start_game()
        else:
            self.start_game()

    def start_game(self):
        """start game"""
        self.dc_recv()
        self.dc_ok()
        self.is_ready_recv()
        self.ready_ok()
        self.get_new_game()


    def __stone_trajectory_parser(self, message_recv: list) -> list:
        """Convert stone trajectory to data class

        Args:
            message_recv (list): List of stone trajectory

        Returns:
            list: List of data classes for stone trajectory
        """
        team_stone: list = []
        for data in message_recv:
            if data is None:
                team_stone.append(Coordinate(angle=None, position=[Position(x=None, y=None)]))

            else:
                team_stone.append(
                    Coordinate(
                        angle=data["angle"],
                        position=[Position(x=data["position"]["x"], y=data["position"]["y"])],
                    )
                )

        return team_stone

    def dc_recv(self):
        """receive dc"""
        message_recv = self.__receive()

        version = Version(
            major=message_recv["version"]["major"],
            minor=message_recv["version"]["minor"],
        )

        dc = ServerDC(
            game_id=message_recv["game_id"],
            cmd=message_recv["cmd"],
            version=version,
            date_time=message_recv["date_time"],
        )

        self.match_data.server_dc = dc

    def dc_ok(self) -> None:
        """send dc_ok"""

        message: dict = {"cmd": "dc_ok", "name": self.client_name}
        message_str: str = json.dumps(message)
        message_str: str = message_str + "\n"
        self.__send(message_str)

    def is_ready_recv(self):
        """receive is_ready"""

        message_recv = self.__receive()

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
            PlayerInfo(
                max_speed=data["max_speed"],
                seed=None,
                stddev_angle=data["stddev_angle"],
                stddev_speed=data["stddev_speed"],
                randomness=data["type"],
            )
            for data in message_recv["game"]["players"]["team0"]
        ]

        team1_players = [
            PlayerInfo(
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
        """send ready_ok"""
        ready = {"cmd": "ready_ok", "player_order": player_order}
        ready_str = json.dumps(ready)
        ready_str = ready_str + "\n"
        self.__send(ready_str)

    def get_new_game(self):
        """receive new_game"""

        message_recv = self.__receive()
        self.match_data.new_game = NewGame(cmd=message_recv["cmd"], name=message_recv["name"])
        if self.match_data.new_game is not None:
            self.is_connected = True

    def update(self):
        """receive update"""

        if self.is_connected is False:
            raise Exception("Not connected to server")
        
        message_recv = self.__receive()

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
            team0=self.__stone_trajectory_parser(message_recv["state"]["stones"]["team0"]),
            team1=self.__stone_trajectory_parser(message_recv["state"]["stones"]["team1"]),
        )

        thinking_time_remaining = ThinkingTimeRemaining(
            team0=message_recv["state"]["thinking_time_remaining"]["team0"],
            team1=message_recv["state"]["thinking_time_remaining"]["team1"],
        )

        if message_recv["last_move"] is None:
            free_guard_zone_foul = False
            type = None
            rotation = None
            x = None
            y = None
            seconds_per_frame = None
        else:
            last_move = message_recv["last_move"]
            actual_move = message_recv["last_move"]["actual_move"]
            free_guard_zone_foul = message_recv["last_move"]["free_guard_zone_foul"]
            type = message_recv["last_move"]["actual_move"]["type"]
            velocity = message_recv["last_move"]["actual_move"]["velocity"]
            rotation = message_recv["last_move"]["actual_move"]["rotation"]
            x = message_recv["last_move"]["actual_move"]["velocity"]["x"]
            y = message_recv["last_move"]["actual_move"]["velocity"]["y"]

            if message_recv["last_move"]["trajectory"] is None:
                seconds_per_frame = None

            else:
                seconds_per_frame = message_recv["last_move"]["trajectory"]["seconds_per_frame"]

                start_team0_position = self.__stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["start"]["team0"]
                )

                start_team1_position = self.__stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["start"]["team1"]
                )

                finish_team0_position = self.__stone_trajectory_parser(
                    message_recv["last_move"]["trajectory"]["finish"]["team0"]
                )

                finish_team1_position = self.__stone_trajectory_parser(
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
                                                x=frame["value"]["position"]["x"],
                                                y=frame["value"]["position"]["y"],
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

    def move(self, x: float = 0.0, y: float = 2.4, rotation: StoneRotation = StoneRotation.outtern) -> None:
        """Shot Stone

        Args:
            x (float, optional): Velocity in x-axis direction. Defaults to 0.0.
            y (float, optional): Velocity in y-axis direction. Defaults to 2.4.
            rotation (str, optional): Direction of rotation. Defaults to "ccw".
        """
        if self.is_connected is False:
            raise Exception("Not connected to server")
        self.move_info.append(
            ShotInfo(
                velocity_x=x,
                velocity_y=y,
                rotation=rotation,
            )
        )

        shot = {
            "cmd": "move",
            "move": {
                "type": "shot",
                "velocity": {"x": x, "y": y},
                "rotation": rotation,
            },
        }
        s = json.dumps(shot)
        s = s + "\n"
        self.__send(s)

    def concede(self) -> None:
        """Concede"""
        concede = {"cmd": "move", "move": {"type": "concede"}}
        s = json.dumps(concede)
        s = s + "\n"
        self.__send(s)

    def get_my_team(self) -> str:
        """get my team name

        Returns:
            str: my team name
        """
        if self.match_data.is_ready is None:
            raise IsReadyNotFoundError("is_ready is None")

        return self.match_data.is_ready.team

    def get_next_team(self) -> str:
        """get next team name"""
        return self.match_data.update_list[-1].next_team

    def get_match_data(self) -> MatchData:
        """get match data"""
        return self.match_data

    def get_winner(self) -> str | None:
        """get winner"""
        if self.match_data.update_list[-1].state.game_result is None:
            raise GameResultNotFoundError("game_result is None")

        return self.match_data.update_list[-1].state.game_result.winner

    def get_move_info(self) -> list[ShotInfo]:
        """get move info"""
        return self.move_info

    def get_update_and_trajectory(self, remove_trajectory: bool = True) -> tuple[list[Update], list[Trajectory]]:
        """get update and trajectory

        Args:
            remove_trajectory (bool, optional): Delete trajectory data from Update?. Defaults to True.

        Returns:
            tuple[list[Update], list[Trajectory]]: update list and trajectory list
        """

        update_list: list[Update] = []
        trajectory_list: list[Trajectory] = []

        for update_data in self.match_data.update_list:
            if update_data.last_move is not None and update_data.last_move.trajectory is not None:
                trajectory_list.append(update_data.last_move.trajectory)

            if remove_trajectory is True:
                data = update_data  # not to change original data
                if data.last_move is not None:
                    data.last_move.trajectory = None
                update_list.append(data)
            else:
                update_list.append(update_data)

        return update_list, trajectory_list

    def get_dc(self) -> ServerDC:
        """get dc data"""
        if self.match_data.server_dc is None:
            raise DCNotFoundError("dc_data is None")
        return self.match_data.server_dc

    def get_is_ready(self) -> IsReady:
        """get is_ready data"""
        if self.match_data.is_ready is None:
            raise IsReadyNotFoundError("is_ready_data is None")
        return self.match_data.is_ready

    def convert_dc(self, dc_data: ServerDC) -> dict[str, Any]:
        """convert ServerDC to dict"""
        dc_dict = {}

        for field in fields(dc_data):
            value = getattr(dc_data, field.name)
            if field.name == "version":
                dc_dict["version"] = {}
                for field in fields(value):
                    dc_version = getattr(value, field.name)
                    dc_dict["version"][field.name] = dc_version
            else:
                dc_dict[field.name] = value
        return dc_dict

    def convert_is_ready(self, is_ready: IsReady) -> dict[str, Any]:
        """convert IsReady to dict

        Args:
            is_ready (IsReady): is_ready

        Returns:
            dict: converted is_ready
        """
        is_ready_dict = {}
        for field in fields(is_ready):
            value = getattr(is_ready, field.name)
            if field.name == "game":
                is_ready_dict[field.name] = {}
                for field in fields(value):
                    game_value = getattr(value, field.name)
                    if field.name == "setting":
                        is_ready_dict["game"][field.name] = {}
                        for field in fields(game_value):
                            config_value = getattr(game_value, field.name)
                            if field.name == "thinking_time":
                                is_ready_dict["game"]["setting"][field.name] = {}
                                for field in fields(config_value):
                                    thinking_time_value = getattr(config_value, field.name)
                                    is_ready_dict["game"]["setting"]["thinking_time"][field.name] = thinking_time_value

                            elif field.name == "extra_end_thinking_time":
                                is_ready_dict["game"]["setting"][field.name] = {}
                                for field in fields(config_value):
                                    extra_end_thinking_time_value = getattr(config_value, field.name)
                                    is_ready_dict["game"]["setting"]["extra_end_thinking_time"][
                                        field.name
                                    ] = extra_end_thinking_time_value

                            else:
                                is_ready_dict["game"]["setting"][field.name] = config_value
                    if field.name == "simulator":
                        is_ready_dict["game"][field.name] = {}
                        for field in fields(game_value):
                            simulator_value = getattr(game_value, field.name)
                            is_ready_dict["game"]["simulator"][field.name] = simulator_value

                    if field.name == "players":
                        is_ready_dict["game"][field.name] = {}
                        for field in fields(game_value):
                            team_data = getattr(game_value, field.name)
                            is_ready_dict["game"]["players"][field.name] = []
                            players_list = []
                            for i in team_data:
                                team_dict = {}
                                for field in fields(i):
                                    normal0 = getattr(i, field.name)
                                    team_dict[field.name] = normal0
                                players_list.append(team_dict)
                            is_ready_dict["game"]["players"][field.name] = players_list

                    else:
                        is_ready_dict["game"][field.name] = game_value
            else:
                is_ready_dict[field.name] = value
        return is_ready_dict

    def convert_update(self, update_data: Update, remove_trajectory: bool = True) -> dict[str, Any]:
        """convert Update to dict

        Args:
            update_data (Update): Update
            remove_trajectory (bool): Delete trajectory data from Update? Defaults to True.

        Returns:
            dict: converted Update
        """
        update_dict = {}
        for field in fields(update_data):
            update_value = getattr(update_data, field.name)
            if field.name == "state":
                update_dict[field.name] = {}
                for field in fields(update_value):
                    state_value = getattr(update_value, field.name)
                    update_dict["state"][field.name] = {}

                    if field.name == "extra_end_score":
                        update_dict["state"][field.name] = {}
                        for field in fields(state_value):
                            extra_end_score_value = getattr(state_value, field.name)
                            update_dict["state"]["extra_end_score"][field.name] = extra_end_score_value

                    elif field.name == "game_result":
                        update_dict["state"][field.name] = {}
                        for field in fields(state_value):
                            game_result_value = getattr(state_value, field.name)
                            update_dict["state"]["game_result"][field.name] = game_result_value

                    elif field.name == "scores":
                        update_dict["state"][field.name] = {}
                        for field in fields(state_value):
                            scores_value = getattr(state_value, field.name)
                            update_dict["state"]["scores"][field.name] = scores_value

                    elif field.name == "stones":
                        for field in fields(state_value):
                            stones_value = getattr(state_value, field.name)
                            update_dict["state"]["stones"][field.name] = []
                            state_stones_team_list = []
                            for i in stones_value:
                                state_stone_team_dict = {}
                                for field in fields(i):
                                    team_value = getattr(i, field.name)
                                    if field.name == "position":
                                        for pos in team_value:
                                            state_stone_team_dict["position"] = {}
                                            for field in fields(pos):
                                                team_position_value = getattr(pos, field.name)
                                                state_stone_team_dict["position"][field.name] = team_position_value

                                    else:
                                        state_stone_team_dict[field.name] = team_value
                                state_stones_team_list.append(state_stone_team_dict)
                            update_dict["state"]["stones"][field.name] = state_stones_team_list

                    elif field.name == "thinking_time_remaining":
                        update_dict["state"][field.name] = {}
                        for field in fields(state_value):
                            thinking_time_remaining_value = getattr(state_value, field.name)
                            update_dict["state"]["thinking_time_remaining"][field.name] = thinking_time_remaining_value

                    else:
                        update_dict["state"][field.name] = state_value

            elif field.name == "last_move":
                if update_value is None:
                    update_dict[field.name] = None
                    continue

                update_dict[field.name] = {}
                for field in fields(update_value):
                    last_move_value = getattr(update_value, field.name)
                    if field.name == "actual_move":
                        update_dict["last_move"][field.name] = {}
                        for field in fields(last_move_value):
                            actual_move_value = getattr(last_move_value, field.name)
                            if field.name == "velocity":
                                update_dict["last_move"]["actual_move"][field.name] = {}
                                for field in fields(actual_move_value):
                                    velocity_value = getattr(actual_move_value, field.name)
                                    update_dict["last_move"]["actual_move"]["velocity"][field.name] = velocity_value
                            else:
                                update_dict["last_move"]["actual_move"][field.name] = actual_move_value

                    elif field.name == "trajectory":
                        if remove_trajectory is True:
                            update_dict["last_move"][field.name] = None
                        else:
                            update_dict["last_move"][field.name] = {}
                            for field in fields(last_move_value):
                                trajectory_value = getattr(last_move_value, field.name)
                                if field.name == "start":
                                    update_dict["last_move"]["trajectory"][field.name] = {}
                                    for field in fields(trajectory_value):
                                        start_value = getattr(trajectory_value, field.name)
                                        update_dict["last_move"]["trajectory"]["start"][field.name] = []
                                        start_team_list = []
                                        for field in fields(start_value):
                                            start_team_dict = {}
                                            start_team_value = getattr(start_value, field.name)
                                            if field.name == "position":
                                                start_team_dict["position"] = {}
                                                for field in fields(start_team_value):
                                                    start_team0_position_value = getattr(start_team_value, field.name)
                                                    start_team_dict["position"][field.name] = start_team0_position_value

                                            else:
                                                start_team_dict[field.name] = start_team_value
                                            start_team_list.append(start_team_dict)
                                        update_dict["last_move"]["trajectory"]["start"][field.name] = start_team_list

                                elif field.name == "finish":
                                    update_dict["last_move"]["trajectory"][field.name] = {}
                                    for field in fields(trajectory_value):
                                        finish_value = getattr(trajectory_value, field.name)
                                        update_dict["last_move"]["trajectory"]["finish"][field.name] = []
                                        finish_team0_list = []
                                        for field in fields(finish_value):
                                            finish_team_dict = {}
                                            finish_team_value = getattr(finish_value, field.name)
                                            if field.name == "position":
                                                finish_team_dict["position"] = {}
                                                for field in fields(finish_team_value):
                                                    finish_team_position_value = getattr(
                                                        finish_team_value,
                                                        field.name,
                                                    )
                                                    finish_team_dict["position"][
                                                        field.name
                                                    ] = finish_team_position_value
                                            else:
                                                finish_team_dict[field.name] = finish_team_value
                                            finish_team0_list.append(finish_team_dict)
                                        update_dict["last_move"]["trajectory"]["finish"][field.name] = finish_team0_list

                                elif field.name == "frames":
                                    update_dict["last_move"]["trajectory"][field.name] = []

                                    for field in fields(trajectory_value):
                                        frames_list = []
                                        frames_dict = {}
                                        frames_value = getattr(trajectory_value, field.name)

                                        if field.name == "value":
                                            frames_dict[field.name] = {}
                                            for field in fields(frames_value):
                                                frames_value_value = getattr(frames_value, field.name)

                                                if field.name == "position":
                                                    frames_dict["value"][field.name] = {}
                                                    for field in fields(frames_value_value):
                                                        frames_value_position_value = getattr(
                                                            frames_value_value,
                                                            field.name,
                                                        )
                                                        frames_dict["value"]["position"][
                                                            field.name
                                                        ] = frames_value_position_value
                                                else:
                                                    frames_dict["value"][field.name] = frames_value_value
                                        else:
                                            frames_dict[field.name] = frames_value

                                        frames_list.append(frames_dict)
                                        update_dict["last_move"]["trajectory"]["frames"].append(frames_list)
                                else:
                                    update_dict["last_move"]["trajectory"][field.name] = trajectory_value
                    else:
                        update_dict["last_move"][field.name] = last_move_value
            else:
                update_dict[field.name] = update_value

        return update_dict

    def convert_trajectory(self, trajectory_data: Trajectory) -> dict[str, Any]:
        """convert trajectory to dict

        Args:
            trajectory_data (Trajectory): trajectory

        Returns:
            dict[str, Any]: dict of trajectory
        """
        trajectory_dict = {}

        for field in fields(trajectory_data):
            value = getattr(trajectory_data, field.name)

            if field.name == "start":
                trajectory_dict[field.name] = {}
                for field in fields(value):
                    start_value = getattr(value, field.name)
                    # if field.name == "team0":
                    trajectory_dict["start"][field.name] = []
                    start_team_list = []
                    for i in start_value:
                        start_team_dict = {}
                        for start_field in fields(i):
                            start_team_value = getattr(i, start_field.name)

                            if start_field.name == "position":
                                for j in start_team_value:
                                    start_team_dict["position"] = {}
                                    for pos_field in fields(j):
                                        start_team_position_value = getattr(j, pos_field.name)
                                        start_team_dict["position"][pos_field.name] = start_team_position_value
                            else:
                                start_team_dict[start_field.name] = start_team_value
                        start_team_list.append(start_team_dict)
                    trajectory_dict["start"][field.name] = start_team_list

            elif field.name == "finish":
                trajectory_dict[field.name] = {}
                for field in fields(value):
                    finish_value = getattr(value, field.name)
                    trajectory_dict["finish"][field.name] = []
                    finish_team_list = []
                    for i in finish_value:
                        finish_team_dict = {}
                        for field in fields(i):
                            finish_team_value = getattr(i, field.name)

                            if field.name == "position":
                                for j in finish_team_value:
                                    finish_team_dict["position"] = {}
                                    for finish_field in fields(j):
                                        finish_team_position_value = getattr(j, finish_field.name)
                                        finish_team_dict["position"][finish_field.name] = finish_team_position_value
                            else:
                                finish_team_dict[field.name] = finish_team_value
                        finish_team_list.append(finish_team_dict)
                    trajectory_dict["finish"][field.name] = finish_team_list

            elif field.name == "frames":
                trajectory_dict[field.name] = []
                for i in value:
                    frames_dict = {}
                    frames_list = []
                    for field in fields(i):
                        frame_value = getattr(i, field.name)
                        if field.name == "value":
                            frames_dict[field.name] = {}
                            for frame_field in fields(frame_value):
                                frame_data_value = getattr(frame_value, frame_field.name)

                                if frame_field.name == "position":
                                    frames_dict["value"][frame_field.name] = {}
                                    for j in frame_data_value:
                                        for frame_field in fields(j):
                                            frame_data_position_value = getattr(j, frame_field.name)
                                            frames_dict["value"]["position"][
                                                frame_field.name
                                            ] = frame_data_position_value

                                else:
                                    frames_dict["value"][frame_field.name] = frame_data_value
                        else:
                            frames_dict[field.name] = frame_value
                    frames_list.append(frames_dict)
                    trajectory_dict["frames"] += frames_list
            else:
                trajectory_dict[field.name] = value
        return trajectory_dict
