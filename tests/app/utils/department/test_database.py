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


class TestGetAllDepartmentsHandler:
    async def test_get_all_departments_no_departments(self, session):
        assert await department.get_all_departments(session=session) == []

    async def test_get_all_departments_ok(self, session, created_department):
        departments = await department.get_all_departments(session=session)
        assert departments
        assert departments == [created_department]

    async def test_get_all_departments_multiple(
        self, session, created_two_departments
    ):
        departments = await department.get_all_departments(session=session)
        assert sorted(departments, key=lambda x: x.name) == sorted(
            created_two_departments, key=lambda x: x.name
        )
