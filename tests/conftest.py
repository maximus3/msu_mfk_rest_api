# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import typing as tp
from asyncio import new_event_loop, set_event_loop
from os import environ
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.config import get_settings
from app.creator import get_app
from app.database.connection import SessionManager
from app.utils import user
from tests.factory_lib import (
    CourseFactory,
    DepartmentFactory,
    StudentCourseFactory,
    StudentFactory,
    UserFactory, StudentDepartmentFactory,
)
from tests.utils import make_alembic_config


@pytest.fixture(scope='session')
def event_loop():
    """
    Creates event loop for tests.
    """
    loop = new_event_loop()
    set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:  # type: ignore
    """
    Создает временную БД для запуска теста.
    """
    settings = get_settings()

    tmp_name = '.'.join([uuid4().hex, 'pytest'])
    settings.POSTGRES_DB = tmp_name
    environ['POSTGRES_DB'] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)


@pytest.fixture
def alembic_config(postgres) -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cmd_options = SimpleNamespace(
        config='',
        name='alembic',
        pg_url=postgres,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


@pytest.fixture
def migrated_postgres(alembic_config: Config):
    """
    Проводит миграции.
    """
    upgrade(alembic_config, 'head')


@pytest.fixture
def create_async_session(  # type: ignore
    migrated_postgres, manager: SessionManager = SessionManager()
) -> tp.Callable:  # type: ignore
    """
    Returns a class object with which you can
    create a new session to connect to the database.
    """
    manager.refresh()  # Very important! Use this in `client` function.
    yield manager.create_async_session


@pytest.fixture
async def session(create_async_session):  # type: ignore
    """
    Creates a new session to connect to the database.
    """
    async with create_async_session() as session:
        yield session


@pytest.fixture
async def client(  # type: ignore
    migrated_postgres, create_async_session
) -> AsyncClient:
    """
    Returns a client that can be used to interact with the application.
    """
    app = get_app()
    yield AsyncClient(app=app, base_url='http://test')


@pytest.fixture
async def potential_user():  # type: ignore
    yield UserFactory.build()


@pytest.fixture
async def not_created_user(potential_user):  # type: ignore
    settings = get_settings()
    yield UserFactory.build(
        username=potential_user.username,
        password=settings.PWD_CONTEXT.hash(potential_user.password),
    )


@pytest.fixture
async def created_user(not_created_user, session):  # type: ignore
    session.add(not_created_user)
    await session.commit()
    await session.refresh(not_created_user)

    yield not_created_user


@pytest.fixture
def user_token(created_user):
    return user.create_access_token(data={'sub': created_user.username})


@pytest.fixture
def user_headers(user_token):
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
async def potential_course():  # type: ignore
    yield CourseFactory.build()


@pytest.fixture
async def not_created_course(potential_course):  # type: ignore
    yield potential_course


@pytest.fixture
async def created_course(not_created_course, session):  # type: ignore
    session.add(not_created_course)
    await session.commit()
    await session.refresh(not_created_course)

    yield not_created_course


@pytest.fixture
async def potential_department():  # type: ignore
    yield DepartmentFactory.build()


@pytest.fixture
async def not_created_department(potential_department):  # type: ignore
    yield potential_department


@pytest.fixture
async def created_department(not_created_department, session):  # type: ignore
    session.add(not_created_department)
    await session.commit()
    await session.refresh(not_created_department)

    yield not_created_department


@pytest.fixture
async def potential_student():  # type: ignore
    yield StudentFactory.build()


@pytest.fixture
async def not_created_student(potential_student):  # type: ignore
    yield potential_student


@pytest.fixture
async def created_student(not_created_student, session):  # type: ignore
    session.add(not_created_student)
    await session.commit()
    await session.refresh(not_created_student)

    yield not_created_student


@pytest.fixture
async def student_course(  # type: ignore
    created_student, created_course, session
):
    relation = StudentCourseFactory.build(
        student_id=created_student.id, course_id=created_course.id
    )
    session.add(relation)
    await session.commit()
    await session.refresh(relation)

    yield relation


@pytest.fixture
async def student_department(  # type: ignore
    created_student, created_department, session
):
    relation = StudentDepartmentFactory.build(
        student_id=created_student.id, department_id=created_department.id
    )
    session.add(relation)
    await session.commit()
    await session.refresh(relation)

    yield relation
