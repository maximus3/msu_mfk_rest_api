from pydantic import BaseModel

from app.schemas.contest.levels import Level


class ContestResults(BaseModel):
    """Contest Results"""

    link: str
    tasks_count: int
    score_max: float
    levels_count: int
    levels: list[Level]
    levels_ok: list[bool]
    lecture: int
    tasks_done: int
    score: float
    score_no_deadline: float
    is_ok: bool
    is_ok_no_deadline: bool
    is_necessary: bool
    is_final: bool
    updated_at: str
    deadline: str


class CourseResults(BaseModel):
    name: str
    contests: list[ContestResults]
    score_sum: float
    score_max: float
    is_ok: bool
    is_ok_final: bool
    perc_ok: int
    str_need: str


class StudentResults(BaseModel):
    courses: list[CourseResults]
    fio: str
