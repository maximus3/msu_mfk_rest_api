from pydantic import BaseModel


class ContestProblem(BaseModel):
    name: str
    alias: str
    id: str
