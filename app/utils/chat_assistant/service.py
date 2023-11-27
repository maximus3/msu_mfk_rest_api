import loguru

from app.config import get_settings
from app.schemas import chat_assistant as chat_assistant_schemas
from app.utils import external_request


async def get_chat_assistant_suggest(
    logger: 'loguru.Logger',
    data: chat_assistant_schemas.ChatAssistantServerRequest,
) -> chat_assistant_schemas.ChatAssistantServerResponse:
    settings = get_settings()
    response = await external_request.make_request(
        url=f'{settings.CHAT_ASSISTANT_API_URL}/api/chat_assistant',
        logger=logger,
        method='POST',
        data=data.dict(),
    )
    logger.info('Chat assistant answer: {}', response.json())
    return chat_assistant_schemas.ChatAssistantServerResponse(
        **response.json()
    )
