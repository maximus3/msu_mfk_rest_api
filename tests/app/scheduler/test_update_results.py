# pylint: disable=too-many-lines
import datetime

import loguru
import pytest

from app.scheduler.update_results import job
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import submission as submission_utils
from app.utils import task as task_utils


pytestmark = pytest.mark.asyncio


@pytest.mark.usefixtures('migrated_postgres', 'mock_send_or_edit')
class TestJob:
    async def test_run(self, mock_bot):
        # arrange

        # act
        await job(base_logger=loguru.logger, save_csv=False)

        # assert
        mock_bot.send_message.assert_not_called()

    @pytest.mark.usefixtures('student_department')
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
                rf'^contests\/'
                rf'{created_contest.yandex_contest_id}\/'
                rf'submissions\?page=1&pageSize=100$': {
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
                rf'^contests\/'
                rf'{created_contest.yandex_contest_id}\/'
                rf'submissions\/multiple\?'
                rf'runIds={1}&runIds={2}$': {
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
                            'submissionTime': (
                                created_contest.deadline
                                - datetime.timedelta(days=1, seconds=2)
                            ).isoformat(),
                            'finalScore': '1',
                        },
                    ],
                },
                rf'^contests\/{created_contest.yandex_contest_id}\/'
                rf'participants\?login={created_student.contest_login}$': {
                    'json': [
                        {
                            'id': '12345',
                        }
                    ]
                },
            }
        )

        # act
        await job(base_logger=loguru.logger, save_csv=False)

        # assert
        mock_bot.send_message.assert_not_called()

        assert (
            created_contest.default_final_score_evaluation_formula
            == created_course.default_final_score_evaluation_formula
        )
        assert (
            created_task.final_score_evaluation_formula
            == created_contest.default_final_score_evaluation_formula
        )

        async with create_async_session(expire_on_commit=False) as session:
            submission_1 = await submission_utils.get_submission(session, 1)
            assert submission_1 is not None
            assert submission_1.final_score == created_task.score_max / 2
            assert submission_1.score_no_deadline == created_task.score_max
            assert submission_1.score_before_finish == 0

            submission_2 = await submission_utils.get_submission(session, 2)
            assert submission_2 is not None
            assert submission_2.final_score == 1
            assert submission_2.score_no_deadline == 1
            assert submission_2.score_before_finish == 1

            student_task = await task_utils.get_student_task_relation(
                session, created_student.id, created_task.id
            )
            assert student_task is not None
            assert student_task.final_score == created_task.score_max / 2
            assert student_task.best_score_no_deadline == 3
            assert student_task.best_score_before_finish == 1
            assert not student_task.is_done
            assert (
                student_task.best_score_before_finish_submission_id
                == submission_2.id
            )
            assert (
                student_task.best_score_no_deadline_submission_id
                == submission_1.id
            )

            student_contest = await contest_utils.get_student_contest_relation(
                session, created_student.id, created_contest.id
            )
            assert student_contest is not None
            assert student_contest.score == created_task.score_max / 2
            assert student_contest.score_no_deadline == created_task.score_max
            assert student_contest.tasks_done == 0
            assert not student_contest.is_ok
            assert student_contest.is_ok_no_deadline

            student_course_model = await course_utils.get_student_course(
                session, created_student.id, created_course.id
            )
            assert student_course_model is not None
            assert student_course_model.score == created_task.score_max / 2
            # assert student_course_model.contests_ok == 0
            # assert not student_course_model.is_ok  # TODO: no levels
            # assert not student_course_model.is_ok_final

    @pytest.mark.usefixtures('student_department')
    async def test_no_verdict_submission(  # pylint: disable=too-many-arguments,unused-argument,too-many-statements  # TODO
        self,
        created_course,
        created_student,
        student_course,
        created_contest,
        created_task,
        created_contest_levels,
        created_zero_submission,
        created_zero_submission_2,
        mock_make_request_to_yandex_contest_v2,
        mock_bot,
        create_async_session,
    ):
        # arrange
        _ = mock_make_request_to_yandex_contest_v2(
            {
                rf'^contests\/{created_contest.yandex_contest_id}\/'
                rf'submissions\?page=1&pageSize=100$': {
                    'json': {
                        'count': 0,
                        'submissions': [],
                    },
                },
                rf'^contests\/{created_contest.yandex_contest_id}\/'
                rf'submissions\/multiple\?runIds='
                rf'{created_zero_submission.run_id}$': {
                    'json': [
                        {
                            'runId': created_zero_submission.run_id,
                            'authorId': created_zero_submission.author_id,
                            'problemId': created_task.yandex_task_id,
                            'problemAlias': created_task.alias,
                            'verdict': 'OK',
                            'participantInfo': {
                                'login': created_student.contest_login,
                            },
                            'submissionTime': (
                                created_contest.deadline
                                + datetime.timedelta(days=1, seconds=1)
                            ).isoformat(),
                            'finalScore': '',
                        },
                    ],
                },
                rf'^contests\/{created_contest.yandex_contest_id}\/'
                rf'submissions\/multiple\?runIds='
                rf'{created_zero_submission_2.run_id}$': {
                    'json': [
                        {
                            'runId': created_zero_submission_2.run_id,
                            'authorId': created_zero_submission_2.author_id,
                            'problemId': created_task.yandex_task_id,
                            'problemAlias': created_task.alias,
                            'verdict': 'OK',
                            'participantInfo': {
                                'login': created_student.contest_login,
                            },
                            'submissionTime': (
                                created_contest.deadline
                                - datetime.timedelta(days=1, seconds=2)
                            ).isoformat(),
                            'finalScore': '1',
                        },
                    ],
                },
                rf'^contests\/{created_contest.yandex_contest_id}\/'
                rf'participants\?login={created_student.contest_login}$': {
                    'json': [{'id': str(created_zero_submission.author_id)}],
                },
            }
        )

        # act
        await job(base_logger=loguru.logger, save_csv=False)

        # assert
        mock_bot.send_message.assert_not_called()

        assert (
            created_contest.default_final_score_evaluation_formula
            == created_course.default_final_score_evaluation_formula
        )
        assert (
            created_task.final_score_evaluation_formula
            == created_contest.default_final_score_evaluation_formula
        )

        async with create_async_session(expire_on_commit=False) as session:
            submission_1 = await submission_utils.get_submission(
                session, created_zero_submission.run_id
            )
            assert submission_1 is not None
            assert submission_1.final_score == created_task.score_max / 2
            assert submission_1.score_no_deadline == created_task.score_max
            assert submission_1.score_before_finish == 0

            submission_2 = await submission_utils.get_submission(
                session, created_zero_submission_2.run_id
            )
            assert submission_2 is not None
            assert submission_2.final_score == 1
            assert submission_2.score_no_deadline == 1
            assert submission_2.score_before_finish == 1

            student_task = await task_utils.get_student_task_relation(
                session, created_student.id, created_task.id
            )
            assert student_task is not None
            assert student_task.final_score == created_task.score_max / 2
            assert student_task.best_score_no_deadline == 3
            assert student_task.best_score_before_finish == 1
            assert not student_task.is_done
            assert (
                student_task.best_score_before_finish_submission_id
                == created_zero_submission_2.id
            )
            assert (
                student_task.best_score_no_deadline_submission_id
                == created_zero_submission.id
            )

            student_contest = await contest_utils.get_student_contest_relation(
                session, created_student.id, created_contest.id
            )
            assert student_contest is not None
            assert student_contest.score == created_task.score_max / 2
            assert student_contest.score_no_deadline == created_task.score_max
            assert student_contest.tasks_done == 0
            assert not student_contest.is_ok
            assert student_contest.is_ok_no_deadline

            student_course_model = await course_utils.get_student_course(
                session, created_student.id, created_course.id
            )
            assert student_course_model is not None
            assert student_course_model.score == created_task.score_max / 2
            # assert student_course_model.contests_ok == 0
            # assert not student_course_model.is_ok  # TODO: no levels
            # assert not student_course_model.is_ok_final
