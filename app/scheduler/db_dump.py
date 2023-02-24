import traceback
import typing as tp
from datetime import datetime
from pathlib import Path

import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app import constants
from app.bot_helper import send
from app.config import DefaultSettings, get_settings
from app.database.connection import SessionManager
from app.schemas import scheduler as scheduler_schemas


TABLE_NAMES = [
    'alembic_version',
    'contest_levels',
    'department',
    'course',
    'course_levels',
    'contest',
    'student',
    'student_department',
    'student_course',
    'student_course_levels',
    'student_contest',
    'student_contest_levels',
    'student_task',
    'submission',
    'task',
    'user',
    'tqdm_logs',
]


async def get_table_data(
    table_name: str,
    settings: DefaultSettings,
    session: AsyncSession | None = None,
) -> tuple[list[str], list[tuple[tp.Any]]]:
    if session is None:
        SessionManager().refresh()
        async with SessionManager().create_async_session() as session:
            return await get_table_data(
                table_name=table_name, settings=settings, session=session
            )
    query = f'SELECT * FROM {table_name}'
    result = await session.execute(query)
    return [
        column[0] for column in result.cursor.description
    ], result.fetchall()


async def dump_table(
    f: tp.TextIO, table_name: str, settings: DefaultSettings
) -> None:
    column_names, rows = await get_table_data(table_name, settings)

    insert_prefix = (
        f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES '
    )
    for row in rows:
        row_data = []
        for rd in row:
            if rd is None:
                row_data.append('NULL')
            elif isinstance(rd, datetime):
                row_data.append(f"'{rd.strftime(constants.dt_format)}'")
            else:
                row_data.append(repr(rd))
        f.write(f'{insert_prefix} ({", ".join(row_data)});\n')


async def job(
    base_logger: 'loguru.Logger', filename: str | None = None
) -> None:
    settings = get_settings()

    formatted_dt = datetime.now().strftime(constants.dt_format_filename)
    filename = filename or f'db_dump_{formatted_dt}.sql'

    base_logger.info('Starting db dump to {}', filename)
    try:
        with open(
            filename,
            'w',
            encoding='utf-8',
        ) as f:
            for table_name in TABLE_NAMES:
                if table_name == 'user':
                    table_name = '"user"'
                await dump_table(f, table_name, settings)
        await send.send_db_dump(filename)
    except Exception as exc:  # pylint: disable=broad-except
        base_logger.exception('Error while dumping db: {}', exc)
        await send.send_traceback_message_safe(
            logger=base_logger,
            message=f'Error while dumping db: {exc}',
            code=traceback.format_exc(),
        )
    finally:
        Path(filename).unlink()


job_info = scheduler_schemas.JobInfo(
    **{
        'func': job,
        'trigger': 'cron',
        'hour': 3,
        'name': 'db_dump',
    },
    config=scheduler_schemas.JobConfig(send_logs=True),
)
