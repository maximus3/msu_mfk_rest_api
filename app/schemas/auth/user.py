from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    username: str
    dt_created: datetime
    dt_updated: datetime

    class Config:
        orm_mode = True
