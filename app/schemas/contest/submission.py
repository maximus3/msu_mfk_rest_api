from pydantic import BaseModel


class ContestSubmission(BaseModel):
    authorId: int
    problemId: str
    verdict: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ContestSubmission):
            return NotImplemented
        return (
            self.authorId == other.authorId
            and self.problemId == other.problemId
            and self.verdict == other.verdict
        )

    def __hash__(self) -> int:
        return hash((self.authorId, self.problemId, self.verdict))
