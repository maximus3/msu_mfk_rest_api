from httpx import AsyncClient, Response

from app.config import get_settings


async def make_request_to_yandex_contest_api(
    endpoint: str, method: str = 'GET'
) -> Response:
    settings = get_settings()
    async with AsyncClient() as client:
        client.headers.update(
            {
                'Authorization': f'OAuth {settings.YANDEX_API_KEY}',
                'Content-Type': 'application/json',
            }
        )
        if method == 'GET':
            response = await client.get(
                f'{settings.YANDEX_CONTEST_API_URL}/{endpoint}'
            )
        elif method == 'POST':
            response = await client.post(
                f'{settings.YANDEX_CONTEST_API_URL}{endpoint}'
            )
        else:
            raise ValueError('Invalid method')
    return response
