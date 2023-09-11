from pydantic import BaseModel


class RegisterRequest(BaseModel):
    fio: str
    department: str
    course: str
    token: str


class RegisterResponse(BaseModel):
    contest_login: str
