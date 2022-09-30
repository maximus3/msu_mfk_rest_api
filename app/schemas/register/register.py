from pydantic import BaseModel


class RegisterRequest(BaseModel):
    fio: str
    department: str
    contest_login: str
    course: str
    token: str


class RegisterResponse(BaseModel):
    contest_login: str
