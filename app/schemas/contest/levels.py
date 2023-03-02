import enum

from pydantic import BaseModel


class LevelOkMethod(str, enum.Enum):
    SCORE_SUM = 'score_sum'
    TASKS_COUNT = 'tasks_count'


class LevelCountMethod(str, enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'


class Level(BaseModel):
    """
    Level of contest.
    """

    name: str
    ok_method: LevelOkMethod
    count_method: LevelCountMethod
    ok_threshold: float | int
    include_after_deadline: bool


class Levels(BaseModel):
    """Levels schema"""

    items: list[Level]
