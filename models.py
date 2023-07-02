from dataclasses import dataclass


@dataclass
class Version:
    major: int
    minor: int


@dataclass  # dcで受信するメッセージを格納
class ServerDC:
    date_time: str
    game_id: str
    cmd: str
    version: Version


@dataclass
class NormalDist:
    """最大速度及び、初速・初期角度に加わる正規分布乱数の標準偏差"""

    max_speed: float
    seed: None
    stddev_angle: float
    stddev_speed: float
    randomness: str


@dataclass
class NormalDist1:
    """最大速度及び、初速・初期角度に加わる正規分布乱数の標準偏差"""

    max_speed: float
    seed: None
    stddev_angle: float
    stddev_speed: float
    randomness: str


@dataclass
class Players:
    """プレイヤーの設定"""

    team0: list[NormalDist]
    team1: list[NormalDist1]


@dataclass
class ExtraEndThinkingTime:
    """延長戦の1エンド毎の思考時間"""

    team0: float
    team1: float


@dataclass
class ThinkingTime:
    """延長戦を含まない思考時間"""

    team0: float
    team1: float


@dataclass
class Setting:
    """試合設定"""

    extra_end_thinking_time: ExtraEndThinkingTime
    five_rock_rule: bool
    max_end: int
    sheet_width: float
    thinking_time: ThinkingTime


@dataclass
class Simulator:
    """シミュレータの設定"""

    seconds_per_frame: float
    simulator_type: str


@dataclass
class GameRule:
    """試合設定"""

    players: Players
    rule: str
    setting: Setting
    simulator: Simulator


@dataclass
class IsReady:
    """対戦開始の際の情報を受け取る(is_ready))"""

    cmd: str
    team: str
    game: GameRule


@dataclass
class NewGame:
    """試合開始の合図"""

    cmd: str
    name: dict


@dataclass
class ExtraEndScore:
    """延長戦のスコア"""

    team0: int
    team1: int


@dataclass
class GameResult:
    winner: str | None
    reason: str | None


@dataclass
class Scores:
    """スコア"""

    team0: list
    team1: list


@dataclass
class Position:
    """位置"""

    x: float | None
    y: float | None


@dataclass
class Coordinate:
    """位置と角度"""

    angle: float | None
    position: list[Position]


@dataclass
class Stones:
    """石の位置"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class ThinkingTimeRemaining:
    """残り思考時間"""

    team0: float
    team1: float


@dataclass
class State:
    """状態"""

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
    x: float | None
    y: float | None


@dataclass
class ActualMove:
    """実際のショット情報"""

    rotation: str | None
    type: str | None
    velocity: Velocity


@dataclass
class Start:
    """ショットの開始位置"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class Finish:
    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass
class Frame:
    """ショットのフレーム情報"""

    team: str | None
    index: int | None
    value: str | None


@dataclass
class Array:
    array: Frame | None


@dataclass
class Trajectory:
    seconds_per_frame: float | None
    start: Start
    finish: Finish
    frames: list[Array] | None


@dataclass
class LastMove:
    """前回のショット情報"""

    actual_move: ActualMove
    free_guard_zone_foul: bool
    trajectory: Trajectory | None


@dataclass
class Update:
    """対戦中の情報を受け取る"""

    cmd: str
    next_team: str
    state: State
    last_move: LastMove | None
