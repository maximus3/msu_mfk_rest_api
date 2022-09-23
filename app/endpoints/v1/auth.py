from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.connection import SessionManager
from app.database.models import User
from app.schemas.auth import Token, UserSchema
from app.utils.user import (
    authenticate_user,
    create_access_token,
    get_current_user,
)


api_router = APIRouter(
    prefix='/user',
    tags=['User'],
)


@api_router.post(
    '/authentication',
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
async def authentication(
    _: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> Token:
    user = await authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')


@api_router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Could not validate credentials',
        },
    },
)
async def get_me(
    _: Request,
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    return UserSchema.from_orm(current_user)
