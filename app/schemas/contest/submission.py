from pydantic import BaseModel


class ContestSubmission(BaseModel):
    authorId: int
    problemId: str
    verdict: str
