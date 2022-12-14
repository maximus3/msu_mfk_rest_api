import logging

import httpx
from httpx import AsyncClient, Response

from app.config import get_settings


async def make_request_to_yandex_contest_api(
    endpoint: str,
    method: str = 'GET',
    timeout: int | None = None,
    retry_count: int = 1,
) -> Response:
    logger = logging.getLogger(__name__)
    settings = get_settings()
    while retry_count > 0:
        async with AsyncClient() as client:
            logger.debug(
                'Making request to Yandex Contest API: %s %s (timeout: %s)',
                method,
                f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
                timeout,
            )
            client.headers.update(
                {
                    'Authorization': f'OAuth {settings.YANDEX_API_KEY}',
                    'Content-Type': 'application/json',
                }
            )
            if method == 'GET':
                try:
                    response = await client.get(
                        f'{settings.YANDEX_CONTEST_API_URL}/{endpoint}',
                        timeout=timeout,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request to Yandex Contest API timed out')
                    retry_count -= 1
                    continue
            elif method == 'POST':
                try:
                    response = await client.post(
                        f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
                        timeout=timeout,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request to Yandex Contest API timed out')
                    retry_count -= 1
                    continue
            else:
                raise ValueError('Invalid method')
            break
    if retry_count == 0:
        raise httpx.ReadTimeout('Request to Yandex Contest API timed out')
    logger.debug(
        'Yandex API request [%s]: %s %s.',
        response.status_code,
        method,
        f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
    )
    return response
