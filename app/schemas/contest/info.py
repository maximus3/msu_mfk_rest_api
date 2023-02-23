from datetime import datetime

from pydantic import BaseModel

from .levels import Levels


class Task(BaseModel):
    yandex_task_id: str
    name: str
    alias: str


class YandexContestInfo(BaseModel):
    deadline: datetime
    tasks_count: int
    duration: int
    tasks: list[Task]


class ContestInfoResponse(BaseModel):
    course_short_name: str | None
    yandex_contest_id: int
    deadline: datetime
    lecture: int
    link: str
    tasks_count: int
    score_max: float
    levels: Levels | None
    is_necessary: bool
