import subprocess
import traceback
from datetime import datetime
from pathlib import Path

import loguru

from app import constants
from app.bot_helper import send
from app.config import get_settings


async def job(
    base_logger: 'loguru.Logger', filename: str | None = None
) -> None:
    settings = get_settings()

    formatted_dt = datetime.now().strftime(constants.dt_format_filename)
    filename = filename or f'db_dump_{formatted_dt}.sql'

    base_logger.info('Starting db dump to {}', filename)

    try:
        command = f'pg_dump --file {filename}'

        proc = subprocess.Popen(
            command,
            shell=True,
            env={
                'PGPASSWORD': settings.POSTGRES_PASSWORD,
                'PGDATABASE': settings.POSTGRES_DB,
                'PGPORT': str(settings.POSTGRES_PORT),
                'PGHOST': settings.POSTGRES_HOST,
                'PGUSER': settings.POSTGRES_USER,
            },
        )
        proc.wait()
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
