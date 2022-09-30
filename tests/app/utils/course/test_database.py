import pytest

from app.utils import course


pytestmark = pytest.mark.asyncio


class TestGetCourseHandler:
    async def test_get_course_no_course(self, session, potential_course):
        assert (
            await course.get_course(
                session=session, name=potential_course.name
            )
            is None
        )

    async def test_get_course_ok(self, session, created_course):
        course_model = await course.get_course(
            session=session, name=created_course.name
        )
        assert course_model
        assert course_model == created_course
