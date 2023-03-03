from pydantic import BaseModel


class CourseNameRequest(BaseModel):
    name: str


class CourseBase(BaseModel):
    name: str
    short_name: str
    channel_link: str
    chat_link: str
    lk_link: str

    class Config:
        orm_mode = True


class CourseResponse(BaseModel):
    items: list[CourseBase]
