# pylint: disable=too-many-arguments,line-too-long,redefined-outer-name

import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def created_course_assist_on(not_created_course, session):  # type: ignore
    not_created_course.is_smart_suggests_allowed = True
    session.add(not_created_course)
    await session.commit()
    await session.refresh(not_created_course)

    yield not_created_course


@pytest.fixture
async def created_course_assist_off(not_created_course, session):  # type: ignore
    not_created_course.is_smart_suggests_allowed = False
    session.add(not_created_course)
    await session.commit()
    await session.refresh(not_created_course)

    yield not_created_course


class TestChatAssistantHandler:
    @staticmethod
    def get_url_application() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/chat_assistant'

    async def test_no_auth(self, client):
        response = await client.post(self.get_url_application())
        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), response.json()

    async def test_no_such_course(
        self, client, user_headers, potential_course
    ):
        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': potential_course.name,
                'contest_number': 1,
                'task_number': 1,
                'user_query': 'query',
            },
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), response.json()
        assert response.json() == {'detail': 'Курс не найден.'}

    async def test_no_such_contest(
        self, client, user_headers, created_course_assist_on, potential_contest
    ):
        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': created_course_assist_on.name,
                'contest_number': potential_contest.lecture,
                'task_number': 1,
                'user_query': 'query',
            },
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), response.json()
        assert response.json() == {
            'detail': f'Контест {potential_contest.lecture} не найден для курса {created_course_assist_on.name}'
        }

    async def test_no_such_task(
        self, client, user_headers, created_course_assist_on, created_contest
    ):
        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': created_course_assist_on.name,
                'contest_number': created_contest.lecture,
                'task_number': 1,
                'user_query': 'query',
            },
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), response.json()
        assert response.json() == {
            'detail': f'В контесте {created_contest.lecture} для курса {created_course_assist_on.name} не найдена задача номер 1'
        }

    async def test_not_allowed(
        self,
        client,
        user_headers,
        created_course_assist_off,
        created_contest,
        created_task,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': created_course_assist_off.name,
                'contest_number': created_contest.lecture,
                'task_number': created_task.alias,
                'user_query': 'query',
            },
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), response.json()
        assert response.json() == {
            'detail': f'Для курса {created_course_assist_off.name} нет умных подсказок.'
        }

    async def test_empty_result(
        self,
        client,
        user_headers,
        created_course_assist_on,
        created_contest,
        created_task,
        mock_make_request,
    ):
        mock_make_request(
            {
                'http://localhost/api/chat_assistant': {
                    'json': {'result': ''},
                },
            }
        )

        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': created_course_assist_on.name,
                'contest_number': created_contest.lecture,
                'task_number': created_task.alias,
                'user_query': 'query',
            },
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), response.json()
        assert response.json() == {
            'detail': 'Error in getting answer, try again later.'
        }

    async def test_ok(
        self,
        client,
        user_headers,
        created_course_assist_on,
        created_contest,
        created_task,
        mock_make_request,
    ):
        mock_make_request(
            {
                'http://localhost/api/chat_assistant': {
                    'json': {'result': 'result here'},
                },
            }
        )

        response = await client.post(
            self.get_url_application(),
            headers=user_headers,
            json={
                'course_name': created_course_assist_on.name,
                'contest_number': created_contest.lecture,
                'task_number': created_task.alias,
                'user_query': 'query',
            },
        )

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json() == {'answer': 'result here'}
