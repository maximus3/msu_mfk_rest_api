import logging

from httpx import AsyncClient, Response

from app.config import get_settings


async def make_request_to_yandex_contest_api(
    endpoint: str, method: str = 'GET', timeout: int | None = None
) -> Response:
    logger = logging.getLogger(__name__)
    settings = get_settings()
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
            response = await client.get(
                f'{settings.YANDEX_CONTEST_API_URL}/{endpoint}',
                timeout=timeout,
            )
        elif method == 'POST':
            response = await client.post(
                f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
                timeout=timeout,
            )
        else:
            raise ValueError('Invalid method')
    logger.debug(
        'Yandex API request [%s]: %s %s.',
        response.status_code,
        method,
        f'{settings.YANDEX_CONTEST_API_URL}{endpoint}',
    )
    return response
