import typing

import httpx
import loguru
from httpx import AsyncClient, Response


async def make_request(  # pylint: disable=too-many-arguments
    url: str,
    logger: 'loguru.Logger',
    method: str = 'GET',
    data: dict[str, typing.Any] | None = None,
    custom_headers: dict[str, str] | None = None,
    timeout: int | None = None,
    retry_count: int = 1,
) -> Response:
    custom_headers = custom_headers or {}
    while retry_count > 0:
        async with AsyncClient() as client:
            logger.info(
                'Making request: {} {} (timeout: {}, data: {})',
                method,
                url,
                timeout,
                data,
            )
            client.headers.update(
                {
                    'Content-Type': 'application/json',
                    **custom_headers,
                }
            )
            if method == 'GET':
                try:
                    response = await client.get(
                        url,
                        timeout=timeout,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request timed out')
                    retry_count -= 1
                    continue
            elif method == 'POST':
                try:
                    response = await client.post(
                        url,
                        json=data,
                        timeout=timeout,
                    )
                except (httpx.ReadTimeout, httpx.ReadError):
                    logger.warning('Request timed out')
                    retry_count -= 1
                    continue
            else:
                raise ValueError('Invalid method')
            break
    if retry_count == 0:
        raise httpx.ReadTimeout('Request timed out')
    logger.info(
        'Request [{}]: {} {}.',
        response.status_code,
        method,
        url,
    )
    return response
