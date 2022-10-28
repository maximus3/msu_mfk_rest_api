from pydantic import BaseModel

from .levels import Levels


class ContestCreateRequest(BaseModel):
    course_short_name: str
    yandex_contest_id: int
    lecture: int
    tasks_need: int
    score_max: float
    levels: Levels | None = None
    is_necessary: bool = True
