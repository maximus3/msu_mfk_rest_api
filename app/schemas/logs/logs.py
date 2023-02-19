from pydantic import BaseModel


class LogItem(BaseModel):
    text: str
    record: dict  # type: ignore


class LogsResponse(BaseModel):
    items: list[LogItem]
    count: int
