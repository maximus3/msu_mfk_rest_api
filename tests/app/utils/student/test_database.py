import pytest

from app.utils import student


pytestmark = pytest.mark.asyncio


class TestGetStudentHandler:
    async def test_get_student_no_student(self, session, potential_student):
        assert (
            await student.get_student(
                session=session, contest_login=potential_student.contest_login
            )
            is None
        )

    async def test_get_student_ok(self, session, created_student):
        student_model = await student.get_student(
            session=session, contest_login=created_student.contest_login
        )
        assert student_model
        assert student_model == created_student
