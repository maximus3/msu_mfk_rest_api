import pytest

from app.utils import department


pytestmark = pytest.mark.asyncio


class TestGetDepartmentHandler:
    async def test_get_department_no_department(
        self, session, potential_department
    ):
        assert (
            await department.get_department(
                session=session, name=potential_department.name
            )
            is None
        )

    async def test_get_department_ok(self, session, created_department):
        department_model = await department.get_department(
            session=session, name=created_department.name
        )
        assert department_model
        assert department_model == created_department
