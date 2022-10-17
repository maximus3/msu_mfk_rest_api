from pydantic import BaseModel

from app.schemas.contest.levels import Level


class ContestResults(BaseModel):
    """Contest Results"""

    link: str
    tasks_count: int
    score_max: float
    levels_count: int
    levels: list[Level]
    lecture: int
    tasks_done: int
    score: float
    is_ok: bool
    updated_at: str


class CourseResults(BaseModel):
    name: str
    contests: list[ContestResults]


class StudentResults(BaseModel):
    courses: list[CourseResults]
