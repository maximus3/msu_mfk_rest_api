from pydantic import BaseModel


class ContestSubmission(BaseModel):
    authorId: int
    problemId: str
    problemAlias: str
    verdict: str
    id: int


class ContestSubmissionFull(ContestSubmission):
    finalScore: int
    login: str
