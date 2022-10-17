from pydantic import BaseModel


class Level(BaseModel):
    """
    Level of contest.
    """

    name: str
    score_need: float


class Levels(BaseModel):
    """Levels schema"""

    count: int
    levels: list[Level]
