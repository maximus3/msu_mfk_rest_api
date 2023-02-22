import datetime as dt

from pydantic import BaseModel


class ContestSubmission(BaseModel):
    id: int
    authorId: int
    problemId: str
    problemAlias: str
    verdict: str


class ContestSubmissionFull(ContestSubmission):
    finalScore: float
    login: str
    timeFromStart: int
    submissionTime: dt.datetime
