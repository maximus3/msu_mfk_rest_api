import loguru

from app.bot_helper import bot
from app.schemas import chat_assistant as chat_assistant_schemas
from app.utils import chat_assistant as chat_assistant_utils


async def task(
    data: chat_assistant_schemas.ChatAssistantServerRequest,
    student_tg_id: str,
    base_logger: 'loguru.Logger',
) -> bool:
    result = await chat_assistant_utils.get_chat_assistant_suggest(
        logger=base_logger,
        data=data,
    )
    if not result.result:
        await bot.bot_students.send_message(
            chat_id=student_tg_id,
            text='Error in getting answer, try again later.',
        )
    await bot.bot_students.send_message(
        chat_id=student_tg_id,
        text=f'Ответ от умного помощника:\n{result.result}',
    )
    return True


async def _send_error_message(
    student_tg_id: str,
    detail: str,
) -> None:
    await bot.bot_students.send_message(
        chat_id=student_tg_id,
        text=detail,
    )
