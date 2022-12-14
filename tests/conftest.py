# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=too-many-lines

import asyncio
import tempfile
import typing as tp
from asyncio import new_event_loop, set_event_loop
from os import environ
from pathlib import Path
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
    ContestFactory,
    CourseFactory,
    DepartmentFactory,
    StudentContestFactory,
    StudentCourseFactory,
    StudentDepartmentFactory,
    StudentFactory,
    UserFactory,
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
async def created_two_courses(session):  # type: ignore
    models = CourseFactory.create_batch(2)
    session.add_all(models)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models])

    yield models


@pytest.fixture
async def created_four_contests_for_two_courses(session, created_two_courses):
    models_1 = ContestFactory.create_batch(
        2, course_id=created_two_courses[0].id
    )
    models_2 = ContestFactory.create_batch(
        2, course_id=created_two_courses[1].id
    )
    session.add_all(models_1)
    session.add_all(models_2)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models_1])
    await asyncio.gather(*[session.refresh(model) for model in models_2])

    yield models_1, models_2


@pytest.fixture
async def created_four_students_for_two_courses(session, created_two_courses):
    models_1 = StudentFactory.create_batch(2)
    models_2 = StudentFactory.create_batch(2)
    session.add_all(models_1)
    session.add_all(models_2)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models_1])
    await asyncio.gather(*[session.refresh(model) for model in models_2])

    models_relations = []
    for i in range(2):
        models_relations.append(
            StudentCourseFactory.build(
                student_id=models_1[i].id, course_id=created_two_courses[0].id
            )
        )
        models_relations.append(
            StudentCourseFactory.build(
                student_id=models_2[i].id, course_id=created_two_courses[1].id
            )
        )
    session.add_all(models_relations)
    await session.commit()

    yield models_1, models_2


@pytest.fixture
async def created_relations_one_student_on_one_contest(
    session,
    created_two_courses,
    created_four_contests_for_two_courses,
    created_four_students_for_two_courses,
):
    models = []
    models.append(
        StudentContestFactory.create(
            course_id=created_two_courses[0].id,
            contest_id=created_four_contests_for_two_courses[0][0].id,
            student_id=created_four_students_for_two_courses[0][0].id,
        )
    )
    models.append(
        StudentContestFactory.create(
            course_id=created_two_courses[1].id,
            contest_id=created_four_contests_for_two_courses[1][0].id,
            student_id=created_four_students_for_two_courses[1][0].id,
        )
    )
    session.add_all(models)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models])

    yield models


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


@pytest.fixture
async def potential_contest(created_course):  # type: ignore
    yield ContestFactory.build(course_id=created_course.id)


@pytest.fixture
async def not_created_contest(potential_contest):  # type: ignore
    yield potential_contest


@pytest.fixture
async def created_contest(not_created_contest, session):  # type: ignore
    session.add(not_created_contest)
    await session.commit()
    await session.refresh(not_created_contest)

    yield not_created_contest


@pytest.fixture
async def created_two_contests(session, created_course):  # type: ignore
    models = ContestFactory.create_batch(2)
    for i in range(2):
        models[i].course_id = created_course.id
    session.add_all(models)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models])

    yield models


@pytest.fixture
async def student_contest(  # type: ignore
    created_student, created_contest, session
):
    relation = StudentContestFactory.build(
        student_id=created_student.id,
        contest_id=created_contest.id,
        course_id=created_contest.course_id,
        is_ok=False,
    )
    session.add(relation)
    await session.commit()
    await session.refresh(relation)

    yield relation


@pytest.fixture
async def student_contest_is_ok(  # type: ignore
    created_student, created_contest, session
):
    relation = StudentContestFactory.build(
        student_id=created_student.id,
        contest_id=created_contest.id,
        course_id=created_contest.course_id,
        is_ok=True,
    )
    session.add(relation)
    await session.commit()
    await session.refresh(relation)

    yield relation


@pytest.fixture
async def mock_make_request_to_yandex_contest(  # type: ignore
    mocker, request=None
):
    objects_to_mock = [
        mocker.patch(
            'app.utils.yandex_request.service'
            '.make_request_to_yandex_contest_api'
        ),
        mocker.patch(
            'app.utils.contest.service.make_request_to_yandex_contest_api',
        ),
    ]
    for obj in objects_to_mock:
        obj.return_value.status_code = (
            request.param if hasattr(request, 'param') else 200
        )
    yield objects_to_mock[0]


@pytest.fixture
async def created_two_departments(session):
    models = DepartmentFactory.create_batch(2)
    session.add_all(models)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models])

    yield models


@pytest.fixture
async def created_two_students_with_course(session, created_course):
    models = StudentFactory.create_batch(2)
    session.add_all(models)
    await session.commit()
    await asyncio.gather(*[session.refresh(model) for model in models])

    relation_models = StudentCourseFactory.create_batch(2)
    for i in range(2):
        relation_models[i].student_id = models[i].id
        relation_models[i].course_id = created_course.id
    session.add_all(relation_models)

    await session.commit()

    yield models


@pytest.fixture
def tmp_file():
    tmp_filename = tempfile.mktemp()
    with open(tmp_filename, 'w', encoding='utf-8') as f:
        f.write('test')
    yield tmp_filename
    Path(tmp_filename).unlink()


@pytest.fixture
def tmp_files():
    tmp_filenames = [tempfile.mktemp() for _ in range(2)]
    for filename in tmp_filenames:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('test')
    yield tmp_filenames
    for filename in tmp_filenames:
        Path(filename).unlink()
