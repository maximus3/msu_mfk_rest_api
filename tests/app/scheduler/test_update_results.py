import datetime

import loguru
import pytest

from app.config import get_settings
from app.scheduler import update_results
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import submission as submission_utils
from app.utils import task as task_utils


pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures('migrated_postgres', 'mock_send_or_edit')
class TestJob:
    async def test_run(self, mock_bot):
        # arrange
        settings = get_settings()

        # act
        await update_results.job(base_logger=loguru.logger)

        # assert
        mock_bot.send_message.assert_called_once_with(
            chat_id=settings.TG_ERROR_CHAT_ID,
            text='Results updated',
            disable_notification=True,
            parse_mode='HTML',
        )

    async def test_ok(  # pylint: disable=too-many-arguments,unused-argument,too-many-statements  # TODO
        self,
        created_course,
        created_student,
        student_course,
        created_contest,
        created_task,
        created_contest_levels,
        mock_make_request_to_yandex_contest_v2,
        mock_bot,
        create_async_session,
    ):
        # arrange
        _ = mock_make_request_to_yandex_contest_v2(
            {
                f'contests/{created_contest.yandex_contest_id}/'
                f'submissions?page=1&pageSize=100': {
                    'json': {
                        'count': 2,
                        'submissions': [
                            {
                                'id': 1,
                                'authorId': 12345,
                                'problemId': created_task.yandex_task_id,
                                'problemAlias': created_task.alias,
                                'verdict': 'OK',
                            },
                            {
                                'id': 2,
                                'authorId': 12345,
                                'problemId': created_task.yandex_task_id,
                                'problemAlias': created_task.alias,
                                'verdict': 'OK',
                            },
                        ],
                    },
                },
                f'contests/{created_contest.yandex_contest_id}/'
                f'submissions/multiple?runIds={1}&runIds={2}': {
                    'json': [
                        {
                            'runId': 1,
                            'authorId': 12345,
                            'problemId': created_task.yandex_task_id,
                            'problemAlias': created_task.alias,
                            'verdict': 'OK',
                            'participantInfo': {
                                'login': created_student.contest_login,
                            },
                            'timeFromStart': 0,  # unused
                            'submissionTime': (
                                created_contest.deadline
                                + datetime.timedelta(days=1, seconds=1)
                            ).isoformat(),
                            'finalScore': '',
                        },
                        {
                            'runId': 2,
                            'authorId': 12345,
                            'problemId': created_task.yandex_task_id,
                            'problemAlias': created_task.alias,
                            'verdict': 'OK',
                            'participantInfo': {
                                'login': created_student.contest_login,
                            },
                            'timeFromStart': 0,  # unused
                            'submissionTime': (
                                created_contest.deadline
                                - datetime.timedelta(days=1, seconds=2)
                            ).isoformat(),
                            'finalScore': '1',
                        },
                    ],
                },
                f'contests/{created_contest.yandex_contest_id}/'
                f'participants?login={created_student.contest_login}': {
                    'text': '12345'
                },
            }
        )
        settings = get_settings()

        # act
        await update_results.job(base_logger=loguru.logger)

        # assert
        mock_bot.send_message.assert_called_once_with(
            chat_id=settings.TG_ERROR_CHAT_ID,
            text='Results updated',
            disable_notification=True,
            parse_mode='HTML',
        )

        async with create_async_session(expire_on_commit=False) as session:
            submission_1 = await submission_utils.get_submission(session, 1)
            assert submission_1 is not None
            assert submission_1.final_score == 0
            assert submission_1.no_deadline_score == created_task.score_max

            submission_2 = await submission_utils.get_submission(session, 2)
            assert submission_2 is not None
            assert submission_2.final_score == 1
            assert submission_2.no_deadline_score == 1

            student_task = await task_utils.get_student_task_relation(
                session, created_student.id, created_task.id
            )
            assert student_task is not None
            assert student_task.final_score == 1
            assert student_task.no_deadline_score == 3
            assert not student_task.is_done
            assert student_task.best_submission_id == submission_2.id
            assert (
                student_task.best_no_deadline_submission_id == submission_1.id
            )

            student_contest = await contest_utils.get_student_contest_relation(
                session, created_student.id, created_contest.id
            )
            assert student_contest is not None
            assert student_contest.score == 1
            assert student_contest.score_no_deadline == created_task.score_max
            assert student_contest.tasks_done == 0
            assert not student_contest.is_ok
            assert student_contest.is_ok_no_deadline

            student_course_model = await course_utils.get_student_course(
                session, created_student.id, created_course.id
            )
            assert student_course_model is not None
            assert student_course_model.score == 1.0
            assert student_course_model.contests_ok == 0
            assert student_course_model.score_percent == 33.3333
            assert student_course_model.contests_ok_percent == 0
            assert not student_course_model.is_ok  # TODO: no levels
            assert not student_course_model.is_ok_final
