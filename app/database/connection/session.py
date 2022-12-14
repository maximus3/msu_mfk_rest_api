import typing as tp
from contextlib import asynccontextmanager, contextmanager

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


class SessionManager:  # pragma: no cover
    """
    A class that implements the necessary
    functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls) -> 'SessionManager':
        if not hasattr(cls, 'instance'):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(bind=self.engine)

    def get_async_session_maker(self) -> sessionmaker:
        return sessionmaker(
            self.async_engine, class_=AsyncSession, expire_on_commit=False
        )

    def refresh(self) -> None:
        settings = get_settings()
        self.engine = sa.create_engine(settings.database_uri_sync)
        self.async_engine = create_async_engine(
            settings.database_uri, echo=True, future=True, pool_pre_ping=True
        )

    @contextmanager
    def create_session(self, **kwargs: tp.Any) -> Session:
        with self.get_session_maker()(**kwargs) as new_session:
            try:
                yield new_session
                new_session.commit()
            except Exception:
                new_session.rollback()
                raise
            finally:
                new_session.close()

    @asynccontextmanager
    async def create_async_session(self, **kwargs: tp.Any) -> AsyncSession:
        async with self.get_async_session_maker()(**kwargs) as new_session:
            try:
                yield new_session
                await new_session.commit()
            except Exception:
                await new_session.rollback()
                raise
            finally:
                await new_session.close()

    async def get_async_session(self) -> AsyncSession:
        async with self.create_async_session() as session:
            yield session
