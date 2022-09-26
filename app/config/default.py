from pathlib import Path

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseSettings, Field


class DefaultSettings(BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments:
    for development, testing and production.
    But in this situation, we only have
    standard settings for local development.
    """

    ENV: str = Field('local', env='ENV')
    PATH_PREFIX: str = Field('/api', env='PATH_PREFIX')
    APP_HOST: str = Field('http://127.0.0.1', env='APP_HOST')
    APP_PORT: int = Field(8090, env='APP_PORT')
    DEBUG: bool = Field(True, env='DEBUG')

    POSTGRES_DB: str = Field('data', env='POSTGRES_DB')
    POSTGRES_HOST: str = Field('localhost', env='POSTGRES_HOST')
    POSTGRES_USER: str = Field('pguser', env='POSTGRES_USER')
    POSTGRES_PORT: int = Field('5432', env='POSTGRES_PORT')
    POSTGRES_PASSWORD: str = Field('pgpswd', env='POSTGRES_PASSWORD')

    LOGGING_FORMAT = (
        '%(filename)s %(funcName)s [LINE:%(lineno)d]# '
        '%(levelname)-8s [%(asctime)s] %(name)s: %(message)s'
    )

    BASE_DIR = Path(__file__).resolve().parent.parent

    # to get a string like this run: "openssl rand -hex 32"
    SECRET_KEY: str = Field('', env='SECRET_KEY')
    ALGORITHM: str = Field('HS256', env='ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        1440, env='ACCESS_TOKEN_EXPIRE_MINUTES'
    )

    PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')

    AUTH_URL = f'/api/v1/user/authentication'
    OAUTH2_SCHEME = OAuth2PasswordBearer(
        tokenUrl=AUTH_URL
    )

    @property
    def database_settings(self) -> dict[str, str | int]:
        """
        Get all settings for connection with database.
        """
        return {
            'database': self.POSTGRES_DB,
            'user': self.POSTGRES_USER,
            'password': self.POSTGRES_PASSWORD,
            'host': self.POSTGRES_HOST,
            'port': self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return (
            'postgresql+asyncpg://{user}:{password}@'
            '{host}:{port}/{database}'.format(
                **self.database_settings,
            )
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return (
            'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
                **self.database_settings,
            )
        )

    class Config:
        env_file: Path | str = '.env'
        env_file_encoding = 'utf-8'
