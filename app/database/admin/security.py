import logging

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database.connection import SessionManager
from app.endpoints import v1
from app.utils import user


class SqlAdminAuthBackend(AuthenticationBackend):
    @SessionManager().with_session
    async def login(  # pylint: disable=arguments-differ
        self,
        request: Request,
        session: AsyncSession,
    ) -> bool:
        logger = logging.getLogger(__name__)
        form = await request.form()
        username, password = form['username'], form['password']
        if not isinstance(username, str) or not isinstance(password, str):
            logger.error(
                'username has type %s, password has type %s',
                type(username),
                type(password),
            )
            return False

        form_data = OAuth2PasswordRequestForm(
            grant_type='password',
            username=username,
            password=password,
            scope='',
            client_id=None,
            client_secret=None,
        )
        try:
            token = await v1.auth.authentication(request, form_data, session)
        except HTTPException:
            return False

        request.session.update({'sqladmin_token': token.access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(  # pylint: disable=arguments-differ
        self,
        request: Request,
    ) -> bool:
        sqladmin_token = request.session.get('sqladmin_token')
        if not sqladmin_token:
            return False

        user_model = await user.get_current_user(sqladmin_token)

        if not user_model:
            return False

        return True
