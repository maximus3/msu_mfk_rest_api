from pydantic import BaseModel


class RegisterHeaders(BaseModel):
    contest_login: str
    bm_id: str
    tg_id: str
    tg_username: str | None
    yandex_id: str
