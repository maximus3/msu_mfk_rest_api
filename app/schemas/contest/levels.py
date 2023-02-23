import enum

from pydantic import BaseModel


class Level(BaseModel):
    """
    Level of contest.
    """

    name: str
    score_need: float | int


class Levels(BaseModel):
    """Levels schema"""

    count: int
    levels: list[Level]


class LevelOkMethod(enum.Enum):
    SCORE_SUM = 'score_sum'
    TASKS_COUNT = 'tasks_count'


class LevelCountMethod(enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'
