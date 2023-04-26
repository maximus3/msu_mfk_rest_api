import loguru
import pytest
from sqlalchemy import select

from app.database import models
from app.scheduler.contest_register_group import job
from app.schemas import contest as contest_schemas
from app.schemas import group as group_schemas
from app.utils import group as group_utils
from tests import factory_lib, utils


pytestmark = pytest.mark.asyncio


class BaseHandler:
    @staticmethod
    async def check_relation_contest_group(
        group_model, contest_model, session
    ):
        contest_group = (
            await session.execute(
                select(models.ContestGroup)
                .where(models.ContestGroup.contest_id == contest_model.id)
                .where(models.ContestGroup.group_id == group_model.id)
            )
        ).scalar_one_or_none()
        return contest_group

    @staticmethod
    async def check_relation_student_group(
        group_model, student_model, session
    ):
        student_group = (
            await session.execute(
                select(models.StudentGroup)
                .where(models.StudentGroup.student_id == student_model.id)
                .where(models.StudentGroup.group_id == group_model.id)
            )
        ).scalar_one_or_none()
        return student_group


@pytest.mark.usefixtures('migrated_postgres')
class TestJob(BaseHandler):
    async def test_run(self, mock_bot):
        # arrange

        # act
        await job(base_logger=loguru.logger)

        # assert
        mock_bot.send_message.assert_not_called()

    async def test_job(
        self,
        mock_make_request_to_yandex_contest_v2,
        mock_bot,
        create_async_session,
    ):
        # arrange
        async with create_async_session(expire_on_commit=False) as session:
            course = await utils.create_model(
                session,
                factory_lib.CourseFactory.build(
                    have_early_exam=True,
                    is_archive=False,
                    is_active=True,
                    is_open_registration=True,
                ),
            )
            student_1 = await utils.create_model(
                session, factory_lib.StudentFactory.build()
            )
            student_2 = await utils.create_model(
                session, factory_lib.StudentFactory.build()
            )
            await utils.create_model(
                session,
                factory_lib.StudentCourseFactory.build(
                    course_id=course.id,
                    student_id=student_1.id,
                    allow_early_exam=True,
                ),
            )
            await utils.create_model(
                session,
                factory_lib.StudentCourseFactory.build(
                    course_id=course.id,
                    student_id=student_2.id,
                    allow_early_exam=False,
                ),
            )
            contest_usual = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[contest_schemas.ContestTag.USUAL],
                ),
            )
            contest_early = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[contest_schemas.ContestTag.EARLY_EXAM],
                ),
            )
            contest_all = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[
                        contest_schemas.ContestTag.USUAL,
                        contest_schemas.ContestTag.EARLY_EXAM,
                    ],
                ),
            )
        mock_make_request_to_yandex_contest_v2(
            {
                r'^groups$': {
                    'json': '{{"id": {randint}}}',
                    'status_code': 201,
                },
                r'^groups\/(.*)\/members$': {'status_code': 204},
                r'^contests\/(.*)\/groups\/(.*)$': {},
            }
        )

        # act
        await job(base_logger=loguru.logger)

        # assert
        mock_bot.send_message.assert_not_called()

        async with create_async_session(expire_on_commit=False) as session:
            groups = await group_utils.get_groups_by_course(session, course.id)
            groups.sort(key=lambda group: group.tags)
            assert len(groups) == 2
            assert list(map(lambda group: group.tags, groups)) == [
                [group_schemas.GroupTag.EARLY_EXAM],
                [group_schemas.GroupTag.USUAL],
            ]

            assert not await self.check_relation_contest_group(
                groups[0], contest_usual, session
            )
            assert await self.check_relation_contest_group(
                groups[0], contest_early, session
            )
            assert await self.check_relation_contest_group(
                groups[0], contest_all, session
            )

            assert await self.check_relation_contest_group(
                groups[1], contest_usual, session
            )
            assert not await self.check_relation_contest_group(
                groups[1], contest_early, session
            )
            assert await self.check_relation_contest_group(
                groups[0], contest_all, session
            )

            assert await self.check_relation_student_group(
                groups[0], student_1, session
            )
            assert not await self.check_relation_student_group(
                groups[0], student_2, session
            )

            assert await self.check_relation_student_group(
                groups[1], student_1, session
            )
            assert await self.check_relation_student_group(
                groups[1], student_2, session
            )
