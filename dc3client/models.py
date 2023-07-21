import enum
from dataclasses import dataclass, field


class StoneRotation(str, enum.Enum):
    """Stone Rotation Direction"""

    # clockwise = "cw"
    # counterclockwise = "ccw"
    intern = "cw"
    outtern = "ccw"


@dataclass
class Version:
    """Version Info"""

    major: int
    minor: int


@dataclass
class ServerDC:
    """Server Info"""

    date_time: str
    game_id: str
    cmd: str
    version: Version


@dataclass
class PlayerInfo:
    """
    Maximum velocity of the stone and standard deviation of normally distributed random numbers
    applied to the initial velocity and initial angle
    """

    max_speed: float
    seed: None
    stddev_angle: float
    stddev_speed: float
    randomness: str


@dataclass
class Players:
    """Pool of players per team"""

    team0: list[PlayerInfo]
    team1: list[PlayerInfo]


@dataclass
class ThinkingTime:
    """Thinking time not including ExtraEnd"""

    team0: float
    team1: float


@dataclass
class ExtraEndThinkingTime:
    """Thinking time per end of ExtraEnd"""

    team0: float
    team1: float


@dataclass
class Setting:
    """Match Setting"""

    extra_end_thinking_time: ExtraEndThinkingTime
    five_rock_rule: bool
    max_end: int
    sheet_width: float
    thinking_time: ThinkingTime


@dataclass
class Simulator:
    """Simulator Settings"""

    seconds_per_frame: float
    simulator_type: str


@dataclass
class GameRule:
    """Game Rule"""

    players: Players
    rule: str
    setting: Setting
    simulator: Simulator


@dataclass
class IsReady:
    """Match settings"""

    cmd: str
    team: str
    game: GameRule


@dataclass
class NewGame:
    """Signal for the start of the match"""

    cmd: str
    name: dict


@dataclass
class ExtraEndScore:
    """ExtraEnd Score"""

    team0: int
    team1: int


@dataclass
class GameResult:
    """Game Result"""

    winner: str | None
    reason: str | None


@dataclass
class Scores:
    """Scores"""

    team0: list
    team1: list


@dataclass
class Position:
    """Stone Position"""

    x: float | None
    y: float | None


@dataclass
class Coordinate:
    """Position and Angle"""

    angle: float | None
    position: list[Position]


@dataclass
class Stones:
    """Stone Positions of each team"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class ThinkingTimeRemaining:
    """Thinking time remaining"""

    team0: float
    team1: float


@dataclass
class State:
    """Match State"""

    end: int
    extra_end_score: ExtraEndScore
    game_result: GameResult
    hammer: str
    scores: Scores
    shot: int
    stones: Stones
    thinking_time_remaining: ThinkingTimeRemaining


@dataclass
class Velocity:
    """Velocity"""

    x: float | None
    y: float | None


@dataclass
class ActualMove:
    """Actual Move"""

    rotation: str | None
    type: str | None
    velocity: Velocity


@dataclass
class Start:
    """Stone placement at the start of the shot"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class Finish:
    """Stone placement at end of shot"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class Frame:
    """
    The position and angle of the stones at each time interval, denoted by seconds_per_frame.
    Each frame is represented as the difference from the previous frame (the first frame is start).
    """

    team: str | None
    index: int | None
    value: Coordinate | None


@dataclass
class FrameArray:
    """Frame Array"""

    array: Frame | None


@dataclass
class Trajectory:
    """Trajectory of each stone"""

    seconds_per_frame: float | None
    start: Start
    finish: Finish
    frames: list[FrameArray] | None


@dataclass
class LastMove:
    """Results of previous shot"""

    actual_move: ActualMove
    free_guard_zone_foul: bool
    trajectory: Trajectory | None


@dataclass
class Update:
    """Match information on each shot"""

    cmd: str
    next_team: str
    state: State
    last_move: LastMove | None


@dataclass
class MatchData:
    """Match Data"""

    server_dc: ServerDC | None = None
    is_ready: IsReady | None = None
    new_game: NewGame | None = None
    update_list: list[Update] = field(default_factory=list)


@dataclass
class ShotInfo:
    """ショット情報"""

    velocity_x: float
    velocity_y: float
    rotation: StoneRotation


class DCNotFoundError(Exception):
    pass


class IsReadyNotFoundError(Exception):
    pass


class GameResultNotFoundError(Exception):
    pass
