# pylint: disable=duplicate-code,too-many-statements

import typing

import httpx
import loguru
from httpx import AsyncClient, Response

from app.config import get_settings


async def make_request_to_yandex_contest_api(  # pylint: disable=too-many-arguments  # noqa: C901
    endpoint: str,
    logger: 'loguru.Logger',
    method: str = 'GET',
    data: dict[str, typing.Any] | None = None,
    timeout: int | None = None,
    retry_count: int = 1,
) -> Response:
    settings = get_settings()
    while retry_count > 0:
        async with AsyncClient() as client:
            logger.info(
                'Making request to Yandex Contest API: '
                '{} {} (timeout: {}, data: {})',
                method,
                f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
                timeout,
                data,
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
                        json=data,
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
    response_data = '*failed to parse response data*'
    try:
        response_data = response.json()
    except Exception:  # pylint: disable=broad-except
        try:
            response_data = response.text
        except Exception:  # pylint: disable=broad-except
            pass
    if len(str(response_data)) > 1024:
        response_data = str(response_data)[:1024] + '... (truncated)'
    try:
        response.raise_for_status()
    except Exception:  # pylint: disable=broad-except
        logger.error(
            'Yandex API request [{}]: {} {}.',
            response.status_code,
            method,
            f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
            body=response_data,
        )
        raise
    logger.info(
        'Yandex API request [{}]: {} {}.',
        response.status_code,
        method,
        f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
        body=response_data,
    )

    return response
