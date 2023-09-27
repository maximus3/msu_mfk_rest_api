import pydantic


class ChatAssistantServerRequest(pydantic.BaseModel):
    contest_number: int
    task_number: str
    user_query: str


class ChatAssistantRequest(pydantic.BaseModel):
    contest_number: int
    task_number: str
    user_query: str
    course_name: str
