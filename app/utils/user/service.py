from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import TokenData

from .database import get_user


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    user = await get_user(session, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    pwd_context = get_settings().PWD_CONTEXT
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    token: str = Depends(get_settings().OAUTH2_SCHEME),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY,
            algorithms=[get_settings().ALGORITHM],
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc
    try:
        async with SessionManager().create_async_session() as session:
            user = await get_user(session, username=token_data.username)
    except Exception as exc:  # pylint: disable=broad-except
        loguru.logger.error('Got get_user exception: type "{}", message "{}"', type(exc), str(exc))
        raise HTTPException(
            status_code=429,
            detail='Too many requests',
        )
    if user is None:
        raise credentials_exception
    return user
