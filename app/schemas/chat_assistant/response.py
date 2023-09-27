import pydantic


class ChatAssistantServerResponse(pydantic.BaseModel):
    result: str


class ChatAssistantResponse(pydantic.BaseModel):
    answer: str
