# pylint: disable=too-many-arguments,too-many-statements

import logging
import time
import traceback
import typing as tp
from pathlib import Path

from aiogram.utils.exceptions import RetryAfter

from app.bot_helper import send_message


def get_need_time(total: int, current: int, avg_speed: float) -> str:
    return time.strftime('%X', time.gmtime((total - current) / avg_speed))


async def tqdm(  # noqa: C901
    iterable: tp.Any,
    total: int | None = None,
    # end='',
    name: str = '',
    logger: logging.Logger | None = None,
    tmp_filename: Path | None = None,
    sql_write_func: tp.Callable[
        [str, int, int | None, str, str, str, str],
        tp.Coroutine[tp.Any, tp.Any, None],
    ]
    | None = None,
    send_or_edit_func: tp.Callable[
        [str, str | None],
        tp.Coroutine[tp.Any, tp.Any, str | None],
    ]
    | None = None,
) -> tp.Any:
    logger = logger or logging.getLogger(__name__)
    if name:
        name_log = '>>' + name + '\t'
    else:
        name_log = ''
    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            total = None
    current = 0
    iter_obj = iter(iterable)
    all_time = '00:00:00'
    avg_speed = 1.0
    start_time = time.time()
    max_len = 0
    message_id = None
    prev_time = start_time - 100
    was_send = False
    while True:
        need_time = get_need_time(total or 0, current, avg_speed)
        need_time_for_all = get_need_time(total or 0, 0, avg_speed)
        avg_data = (
            f'{1 / avg_speed:.2f} s/it'
            if avg_speed < 1
            else f'{avg_speed:.2f} it/s'
        )
        text = (
            f'{name_log}[{current}/{total}]\t{all_time}/'
            f'{need_time_for_all}\t{avg_data}\t{need_time}'
        )
        max_len = max(max_len, len(text) + 24)
        if logger:
            logger.info(text)
        if sql_write_func:
            pass  # TODO: TooManyClients
            # await sql_write_func(
            #     name,
            #     current,
            #     total,
            #     need_time,
            #     need_time_for_all,
            #     avg_data,
            #     all_time,
            # )
        # else:
        #     print('\r', ' ' * max_len, '\r', sep='', end='')
        #     print(f'\r{text}\r', end=end)
        if send_or_edit_func:
            if time.time() - prev_time > 10:
                try:
                    prev_time = time.time()
                    message_id = await send_or_edit_func(text, message_id)
                    was_send = True
                except RetryAfter:
                    pass
                except Exception as exc:
                    await send_message(
                        f'Error while send_or_edit_func (message_id={message_id}):\n'
                        f': {exc}\n{traceback.format_exc()}'
                    )
            else:
                was_send = False
        if tmp_filename:
            with open(tmp_filename, 'w', encoding='utf-8') as f:
                f.write(text)
        try:
            current += 1
            yield next(iter_obj)
            avg_speed = current / max(0.001, time.time() - start_time)
            all_time = time.strftime(
                '%X', time.gmtime(time.time() - start_time)
            )
        except StopIteration:
            if not was_send:
                try:
                    message_id = await send_or_edit_func(text, message_id)
                except RetryAfter:
                    pass
                except Exception as exc:
                    await send_message(
                        f'Error while send_or_edit_func (message_id={message_id}):\n'
                        f': {exc}\n{traceback.format_exc()}'
                    )
            break

    if tmp_filename:
        tmp_filename.unlink()
