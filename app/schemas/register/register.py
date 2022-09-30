from pydantic import BaseModel


class RegisterRequest(BaseModel):
    fio: str
    department: str
    login: str
    course: str
    token: str
