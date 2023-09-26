# pylint: disable=too-many-arguments, unused-argument, too-many-public-methods

import pytest
from fastapi import status

from app.config import get_settings
from app.endpoints.v1 import prefix


pytestmark = pytest.mark.asyncio


class TestRegisterHandler:
    @staticmethod
    def get_url_application() -> str:
        settings = get_settings()
        return f'{settings.PATH_PREFIX}{prefix}/register'

    @staticmethod
    def get_data(student, department, course):
        return {
            'fio': student.fio,
            'department': department.name,
            'course': course.name,
            'token': student.token,
        }

    @staticmethod
    def _get_headers(student, user_headers):
        return {
            'log-contest-login': student.contest_login,
            'log-tg-id': student.tg_id,
            'log-tg-username': student.tg_username,
            'log-bm-id': student.bm_id,
            'log-yandex-id': student.yandex_id,
            **user_headers,
        }

    async def test_register_no_auth(self, client):
        response = await client.post(self.get_url_application())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_register_no_data(
        self, client, user_headers, potential_student
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=potential_student, user_headers=user_headers
            ),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_no_fio(
        self,
        client,
        user_headers,
        potential_student,
        created_department,
        created_course,
    ):
        data = self.get_data(
            potential_student, created_department, created_course
        )
        data.pop('fio')
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=potential_student, user_headers=user_headers
            ),
            json=data,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_already_registered(
        self,
        client,
        user_headers,
        created_student,
        created_course,
        created_department,
        student_course,
        student_department,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=created_student, user_headers=user_headers
            ),
            json=self.get_data(
                created_student, created_department, created_course
            ),
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            'detail': 'Student already registered on course'
        }

    async def test_register_already_registered_second_query(
        self,
        client,
        user_headers,
        created_student,
        created_course,
        created_department,
        student_department,
    ):
        data = self.get_data(
            created_student, created_department, created_course
        )
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=created_student, user_headers=user_headers
            ),
            json=data,
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=created_student, user_headers=user_headers
            ),
            json=data,
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            'detail': 'Student already registered on course'
        }

    async def test_register_no_such_department(
        self,
        client,
        user_headers,
        potential_student,
        potential_department,
        created_course,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=potential_student, user_headers=user_headers
            ),
            json=self.get_data(
                potential_student, potential_department, created_course
            ),
        )
        assert response.status_code == 404
        assert response.json() == {'detail': 'Department not found'}

    async def test_register_no_such_course(
        self,
        client,
        user_headers,
        potential_student,
        created_department,
        potential_course,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=potential_student, user_headers=user_headers
            ),
            json=self.get_data(
                potential_student, created_department, potential_course
            ),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {'detail': 'Course not found'}

    async def test_register_ok_no_student(
        self,
        client,
        user_headers,
        potential_student,
        created_department,
        created_course,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=potential_student, user_headers=user_headers
            ),
            json=self.get_data(
                potential_student, created_department, created_course
            ),
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'contest_login': potential_student.contest_login
        }

    async def test_register_ok_with_student(
        self,
        client,
        user_headers,
        created_student,
        created_department,
        created_course,
    ):
        response = await client.post(
            self.get_url_application(),
            headers=self._get_headers(
                student=created_student, user_headers=user_headers
            ),
            json=self.get_data(
                created_student, created_department, created_course
            ),
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'contest_login': created_student.contest_login
        }

    async def test_register_new_yandex_id(
        self,
        client,
        user_headers,
        created_student,
        created_department,
        created_course,
    ):
        headers = self._get_headers(
            student=created_student, user_headers=user_headers
        )
        headers['log-yandex-id'] = headers['log-yandex-id'] + '-another'
        response = await client.post(
            self.get_url_application(),
            headers=headers,
            json=self.get_data(
                created_student, created_department, created_course
            ),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'Кажется, вы пытаетесь зарегистрироваться '
            'на курс не через тот же яндекс аккаунт, через '
            'который регистрировались до этого. Если вы '
            'по каким-то причинам хотите поменять аккаунт, '
            'то напишите в поддержку.',
        }

    async def test_register_from_another_tg(
        self,
        client,
        user_headers,
        created_student,
        created_department,
        created_course,
    ):
        headers = self._get_headers(
            student=created_student, user_headers=user_headers
        )
        headers['log-tg-id'] = headers['log-tg-id'] + '-another'
        response = await client.post(
            self.get_url_application(),
            headers=headers,
            json=self.get_data(
                created_student, created_department, created_course
            ),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            'detail': 'Кажется, вы пытаетесь зарегистрироваться '
            'на курс не через тот же телеграм аккаунт, через '
            'который регистрировались до этого. Если вы '
            'по каким-то причинам хотите поменять аккаунт, '
            'то напишите в поддержку.',
        }
