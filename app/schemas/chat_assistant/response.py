import pydantic


class ChatAssistantServerResponse(pydantic.BaseModel):
    result: str | None = None
    error: str | None = None


class ChatAssistantResponse(pydantic.BaseModel):
    answer: str
