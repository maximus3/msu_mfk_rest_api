from pydantic import BaseModel


class ContestResults(BaseModel):
    """Contest Results"""

    link: str
    tasks_count: int
    tasks_need: int
    tasks_done: int
    is_ok: bool
    updated_at: str


class CourseResults(BaseModel):
    name: str
    contests: list[ContestResults]


class StudentResults(BaseModel):
    courses: list[CourseResults]
