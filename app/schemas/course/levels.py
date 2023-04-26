import enum

from pydantic import BaseModel

from app.schemas import contest as contest_schemas


class LevelOkMethod(str, enum.Enum):
    CONTESTS_OK = 'contests_ok'
    SCORE_SUM = 'score_sum'


class LevelCountMethod(str, enum.Enum):
    ABSOLUTE = 'absolute'
    PERCENT = 'percent'


class LevelInfoElem(BaseModel):
    level_ok_method: LevelOkMethod
    count_method: LevelCountMethod
    ok_threshold: float
    contest_ok_level_name: str | None
    tags: list[contest_schemas.ContestTag] | None


class LevelInfo(BaseModel):
    data: list[LevelInfoElem]
