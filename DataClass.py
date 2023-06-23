from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Version:
    major : int
    minor : int


@dataclass_json
@dataclass  # dcで受信するメッセージを格納
class server_dc:
    cmd: str
    version: Version
    game_id: str
    date_time: str


@dataclass_json
@dataclass
class NormalDist:
    """最大速度及び、初速・初期角度に加わる正規分布乱数の標準偏差"""

    max_speed: float
    seed: None
    stddev_angle: float
    stddev_speed: float
    type: str



@dataclass_json
@dataclass
class Players:
    """プレイヤーの設定"""

    team0: list[NormalDist]
    team1: list[NormalDist]


@dataclass_json
@dataclass
class ExtraEndThinkingTime:
    """延長戦の1エンド毎の思考時間"""

    team0: float
    team1: float


@dataclass_json
@dataclass
class ThinkingTime:
    """延長戦を含まない思考時間"""

    team0: float
    team1: float


@dataclass_json
@dataclass
class Setting:
    """試合設定"""

    extra_end_thinking_time: ExtraEndThinkingTime
    five_rock_rule: bool
    max_end: int
    sheet_width: float
    thinking_time: ThinkingTime


@dataclass_json
@dataclass
class Simulator:
    """シミュレータの設定"""

    seconds_per_frame: float
    simulator_type: str


@dataclass_json
@dataclass
class gamerule:
    """試合設定"""

    players: Players
    rule: str
    setting: Setting
    simulator: Simulator


@dataclass_json
@dataclass
class isready:
    """対戦開始の際の情報を受け取る(is_ready))"""

    cmd: str
    team: str
    game: gamerule


@dataclass_json
@dataclass
class NewGame:
    """試合開始の合図"""

    cmd: str
    name: dict


@dataclass_json
@dataclass
class ExtraEndScore:
    """延長戦のスコア"""

    team0: int
    team1: int


@dataclass_json
@dataclass
class GameResult:
    winner: str | None
    reason: str | None


@dataclass_json
@dataclass
class Scores:
    """スコア"""

    team0: list
    team1: list


@dataclass_json
@dataclass
class Position:
    """位置"""

    x: float
    y: float


@dataclass_json
@dataclass
class Coordinate:
    """位置と角度"""

    angle: float
    position: list[Position]


@dataclass_json
@dataclass
class Stones:
    """石の位置"""

    team0: list[Coordinate]
    team1: list[Coordinate]


@dataclass_json
@dataclass
class ThinkingTimeRemaining:
    """残り思考時間"""

    team0: float
    team1: float


@dataclass_json
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


@dataclass_json
@dataclass
class Velocity:
    x : float | None
    y : float | None


@dataclass_json
@dataclass
class ActualMove:
    """実際のショット情報"""

    rotation: str | None
    type: str | None
    velocity: Velocity


@dataclass_json
@dataclass
class LastMove:
    """前回のショット情報"""

    actual_move: ActualMove
    free_guard_zone_foul : bool


@dataclass_json
@dataclass
class Update:
    """対戦中の情報を受け取る"""

    cmd: str
    next_team: str
    state: State
    last_move : LastMove
