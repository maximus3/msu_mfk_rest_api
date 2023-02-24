import typing as tp

from pydantic import BaseModel


class JobConfig(BaseModel):
    send_logs: bool


class JobInfo(BaseModel):
    func: tp.Any
    trigger: str
    name: str
    minutes: int | None
    hours: int | None
    hour: int | None
    config: JobConfig | None
