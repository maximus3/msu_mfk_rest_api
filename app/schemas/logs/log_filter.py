from pydantic import BaseModel


class LogFilter(BaseModel):
    json_path: str
    value: str
