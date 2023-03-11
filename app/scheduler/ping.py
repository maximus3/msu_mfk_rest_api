import traceback
from collections import defaultdict
from itertools import product

import loguru
from httpx import AsyncClient

from app.bot_helper import send
from app.config import get_settings
from app.endpoints.v1 import prefix


async def job(base_logger: 'loguru.Logger') -> None:
    settings = get_settings()

    base_url = f'http://{{}}{settings.PATH_PREFIX}{prefix}/health_check/{{}}'
    hosts = [
        f'nginx:{settings.NGINX_EXTERNAL_PORT}',
        f'app:{settings.APP_PORT}',
    ]
    endpoints = ['ping_database', 'ping_application']

    result: dict[str, dict[str, str]] = defaultdict(dict)

    async with AsyncClient() as client:
        for host, endpoint in product(hosts, endpoints):
            try:
                response = await client.get(base_url.format(host, endpoint))
                if response.status_code != 200:
                    base_logger.error(
                        'Health check "{}" on {} failed '
                        'with status code {}',
                        host,
                        endpoint,
                        response.status_code,
                    )
                    result[host][
                        endpoint
                    ] = f'Failed (status code: {response.status_code})'
                    continue
                base_logger.info(
                    'Health check "{}" on {} is successful', host, endpoint
                )
                result[host][endpoint] = 'Successful'
            except Exception as e:  # pylint: disable=broad-except
                base_logger.error(
                    'Health check "{}" on {} failed (url "{}"): {}',
                    host,
                    endpoint,
                    base_url.format(host, endpoint),
                    e,
                )
                result[host][endpoint] = (
                    f'Failed (url "{base_url.format(host, endpoint)}"): '
                    f'{e}'
                )

    try:
        await send.send_ping_status(result)
    except Exception as exc:  # pylint: disable=broad-except
        base_logger.error('Failed to send ping status: {}', exc)
        await send.send_traceback_message_safe(
            logger=base_logger,
            message=f'Failed to send ping status: {exc}',
            code=traceback.format_exc(),
        )
