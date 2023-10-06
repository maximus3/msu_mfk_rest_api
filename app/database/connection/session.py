import functools
import typing as tp
from contextlib import asynccontextmanager, contextmanager

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


class SessionManager:  # pragma: no cover
    """
    A class that implements the necessary
    functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    ENGINE_KWARGS = {
        'max_overflow': 0,
        'pool_size': 1,
        'pool_timeout': 60,
    }

    def __new__(cls) -> 'SessionManager':
        if not hasattr(cls, 'instance'):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    def refresh(self) -> None:
        pass

    def get_async_engine(self) -> AsyncEngine:
        settings = get_settings()
        return create_async_engine(
            settings.database_uri,
            future=True,
            pool_pre_ping=True,
            **self.ENGINE_KWARGS,
        )

    @contextmanager
    def create_session(self, **kwargs: tp.Any) -> Session:
        settings = get_settings()
        engine = sa.create_engine(
            settings.database_uri_sync,
            **self.ENGINE_KWARGS,
        )
        with sessionmaker(bind=engine)(**kwargs) as new_session:
            try:
                yield new_session
                new_session.commit()
            except Exception:
                new_session.rollback()
                raise
            finally:
                new_session.close()
        engine.dispose()

    @asynccontextmanager
    async def create_async_session(self, **kwargs: tp.Any) -> AsyncSession:
        settings = get_settings()
        async_engine = create_async_engine(
            settings.database_uri,
            future=True,
            pool_pre_ping=True,
            **self.ENGINE_KWARGS,
        )

        async with sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )(**kwargs) as new_session:
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

    def with_session(self, func: tp.Callable) -> tp.Callable:  # type: ignore
        @functools.wraps(func)
        async def wrapper(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            async with self.create_async_session() as session:
                return await func(*args, session=session, **kwargs)

        return wrapper
