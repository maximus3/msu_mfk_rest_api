import logging
from collections import defaultdict
from itertools import product

from httpx import AsyncClient

from app.bot_helper import send_ping_status
from app.config import get_settings
from app.endpoints.v1 import prefix


async def job() -> None:
    settings = get_settings()
    logger = logging.getLogger(__name__)

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
                    logger.error(
                        'Health check "%s" on %s failed '
                        'with status code %s',
                        host,
                        endpoint,
                        response.status_code,
                    )
                    result[host][
                        endpoint
                    ] = f'Failed (status code: {response.status_code})'
                    continue
                logger.info(
                    'Health check "%s" on %s is successful', host, endpoint
                )
                result[host][endpoint] = 'Successful'
            except Exception as e:  # pylint: disable=broad-except
                logger.error(
                    'Health check "%s" on %s failed (url "%s"): %s',
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
        await send_ping_status(result)
    except Exception as e:
        logger.error('Failed to send ping status: %s', e)
        raise e


job_info = {
    'func': job,
    'trigger': 'interval',
    'minutes': 1,
    'name': 'ping_app',
}
