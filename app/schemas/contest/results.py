from pydantic import BaseModel


class ContestResults(BaseModel):
    keys: list[str]
    results: dict[str, dict[str, str | bool]]
