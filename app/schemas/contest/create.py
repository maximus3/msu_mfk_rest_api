from pydantic import BaseModel

from .levels import Levels


class ContestCreateRequest(BaseModel):
    course_short_name: str
    yandex_contest_id: int
    lecture: int
    score_max: float
    levels: Levels | None = None
    is_necessary: bool = True
    is_final: bool = False
    is_usual: bool = True
    is_early_exam: bool = False
    default_final_score_evaluation_formula: str | None = None
    name_format: str | None = None
