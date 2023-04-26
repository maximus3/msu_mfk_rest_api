from pydantic import BaseModel


class LevelWithOk(BaseModel):
    name: str
    is_ok: bool
    score_need: float
    include_after_deadline: bool


class ContestResults(BaseModel):
    """Contest Results"""

    link: str
    tasks_count: int
    score_max: float
    levels_count: int
    levels: list[LevelWithOk]
    lecture: int
    tasks_done: int
    score: float
    score_no_deadline: float
    is_ok: bool
    is_ok_no_deadline: bool
    is_necessary: bool
    is_final: bool
    name: str
    updated_at: str
    deadline: str


class CourseLevelResults(BaseModel):
    """Course Level Results"""

    name: str
    is_ok: bool


class CourseResults(BaseModel):
    name: str
    contests: list[ContestResults]
    score_sum: float
    score_sum_no_deadline: float
    score_max: float
    is_ok: bool
    is_ok_final: bool
    early_exam: bool
    perc_ok: int
    str_need: str
    course_levels: list[CourseLevelResults]


class StudentResults(BaseModel):
    courses: list[CourseResults]
    fio: str
