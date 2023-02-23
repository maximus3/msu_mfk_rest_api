import typing as tp

from pydantic import BaseModel


class JobInfo(BaseModel):
    func: tp.Any
    trigger: str
    name: str
    minutes: int | None
    hours: int | None
    hour: int | None
