from enum import Enum, unique

from pydantic import BaseModel


@unique
class PingMessage(str, Enum):
    OK = 'Application worked!'
    DB_ERROR = "Database isn't working"


class PingResponse(BaseModel):
    message: PingMessage
    detail: str | None
