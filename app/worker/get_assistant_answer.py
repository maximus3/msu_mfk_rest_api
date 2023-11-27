import loguru

from app.bot_helper import send
from app.schemas import chat_assistant as chat_assistant_schemas
from app.utils import chat_assistant as chat_assistant_utils


async def task(
    data_raw: dict[str, str | int],
    base_logger: 'loguru.Logger',
) -> list[str]:
    data = chat_assistant_schemas.ChatAssistantServerRequest(
        **data_raw,
    )
    result = await chat_assistant_utils.get_chat_assistant_suggest(
        logger=base_logger,
        data=data,
    )
    if result.error:
        await send.send_message_safe(
            logger=base_logger,
            message=f'Got error in chat assistant response: {result.error}',
        )
    if not result.result:
        return ['Error in getting answer, try again later.']
    return [result.result]
