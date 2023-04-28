# pylint: disable=too-many-lines,duplicate-code
import datetime

import loguru
import pytest

from app.scheduler.update_results import job
from app.schemas import contest as contest_schemas
from app.utils import contest as contest_utils
from app.utils import course as course_utils
from app.utils import submission as submission_utils
from app.utils import task as task_utils
from tests import factory_lib, utils


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

    async def test_with_tags(  # pylint: disable=too-many-statements
        self,
        mock_make_request_to_yandex_contest_v2,
        mock_bot,
        create_async_session,
    ):
        # arrange
        async with create_async_session(expire_on_commit=False) as session:
            # course
            course = await utils.create_model(
                session,
                factory_lib.CourseFactory.build(
                    have_early_exam=True,
                    is_archive=False,
                    is_active=True,
                    is_open_registration=True,
                    default_final_score_evaluation_formula='max('
                    '{best_score_before_finish}, '
                    '{best_score_no_deadline} / 2)',
                    contest_count=3,
                    score_max=30,
                ),
            )

            # students
            student_1 = await utils.create_model(
                session,
                factory_lib.StudentFactory.build(contest_login='student_1'),
            )
            student_2 = await utils.create_model(
                session,
                factory_lib.StudentFactory.build(contest_login='student_2'),
            )
            await utils.create_model(
                session,
                factory_lib.StudentCourseFactory.build(
                    course_id=course.id,
                    student_id=student_1.id,
                    allow_early_exam=True,
                    score=0,
                    score_no_deadline=0,
                    contests_ok=0,
                    is_ok=False,
                    is_ok_final=False,
                ),
            )
            await utils.create_model(
                session,
                factory_lib.StudentCourseFactory.build(
                    course_id=course.id,
                    student_id=student_2.id,
                    allow_early_exam=False,
                    score=0,
                    score_no_deadline=0,
                    contests_ok=0,
                    is_ok=False,
                    is_ok_final=False,
                ),
            )

            # contests
            contest_base = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[
                        contest_schemas.ContestTag.USUAL,
                        contest_schemas.ContestTag.EARLY_EXAM,
                        contest_schemas.ContestTag.NECESSARY,
                    ],
                    default_final_score_evaluation_formula=course.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                    score_max=10,
                    yandex_contest_id=1,
                    tasks_count=1,
                ),
            )
            contest_early_final = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[
                        contest_schemas.ContestTag.EARLY_EXAM,
                        contest_schemas.ContestTag.FINAL,
                    ],
                    default_final_score_evaluation_formula=course.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                    score_max=15,
                    yandex_contest_id=2,
                    tasks_count=1,
                ),
            )
            contest_usual_final = await utils.create_model(
                session,
                factory_lib.ContestFactory.build(
                    course_id=course.id,
                    tags=[
                        contest_schemas.ContestTag.USUAL,
                        contest_schemas.ContestTag.FINAL,
                    ],
                    default_final_score_evaluation_formula=course.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                    score_max=5,
                    yandex_contest_id=3,
                    tasks_count=1,
                ),
            )

            # tasks
            task_base = await utils.create_model(
                session,
                factory_lib.TaskFactory.build(
                    contest_id=contest_base.id,
                    score_max=10,
                    is_zero_ok=True,
                    final_score_evaluation_formula=contest_base.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                ),
            )
            task_early_final = await utils.create_model(
                session,
                factory_lib.TaskFactory.build(
                    contest_id=contest_early_final.id,
                    score_max=15,
                    is_zero_ok=True,
                    final_score_evaluation_formula=contest_early_final.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                ),
            )
            task_usual_final = await utils.create_model(
                session,
                factory_lib.TaskFactory.build(
                    contest_id=contest_usual_final.id,
                    score_max=5,
                    is_zero_ok=True,
                    final_score_evaluation_formula=contest_usual_final.default_final_score_evaluation_formula,  # pylint: disable=line-too-long
                ),
            )

            # contest_levels
            contest_base_levels = [
                await utils.create_model(
                    session,
                    factory_lib.ContestLevelsFactory.build(
                        course_id=course.id,
                        contest_id=contest_base.id,
                        level_name='Зачет автоматом',
                        level_ok_method=contest_schemas.LevelOkMethod.SCORE_SUM,  # pylint: disable=line-too-long
                        count_method=contest_schemas.LevelCountMethod.PERCENT,
                        ok_threshold=100,
                        include_after_deadline=False,
                    ),
                ),
                await utils.create_model(
                    session,
                    factory_lib.ContestLevelsFactory.build(
                        course_id=course.id,
                        contest_id=contest_base.id,
                        level_name='Допуск к зачету',
                        level_ok_method=contest_schemas.LevelOkMethod.SCORE_SUM,  # pylint: disable=line-too-long
                        count_method=contest_schemas.LevelCountMethod.PERCENT,
                        ok_threshold=100,
                        include_after_deadline=True,
                    ),
                ),
                await utils.create_model(
                    session,
                    factory_lib.ContestLevelsFactory.build(
                        course_id=course.id,
                        contest_id=contest_base.id,
                        level_name='Допуск к досрочному зачету',
                        level_ok_method=contest_schemas.LevelOkMethod.SCORE_SUM,  # pylint: disable=line-too-long
                        count_method=contest_schemas.LevelCountMethod.PERCENT,
                        ok_threshold=100,
                        include_after_deadline=True,
                    ),
                ),
            ]
            contest_early_final_levels = [
                await utils.create_model(
                    session,
                    factory_lib.ContestLevelsFactory.build(
                        course_id=course.id,
                        contest_id=contest_early_final.id,
                        level_name='Зачет',
                        level_ok_method=contest_schemas.LevelOkMethod.SCORE_SUM,  # pylint: disable=line-too-long
                        count_method=contest_schemas.LevelCountMethod.PERCENT,
                        ok_threshold=100,
                        include_after_deadline=False,
                    ),
                ),
            ]
            contest_usual_final_levels = [
                await utils.create_model(
                    session,
                    factory_lib.ContestLevelsFactory.build(
                        course_id=course.id,
                        contest_id=contest_usual_final.id,
                        level_name='Зачет',
                        level_ok_method=contest_schemas.LevelOkMethod.SCORE_SUM,  # pylint: disable=line-too-long
                        count_method=contest_schemas.LevelCountMethod.PERCENT,
                        ok_threshold=100,
                        include_after_deadline=False,
                    ),
                ),
            ]

            # student_contests
            contest_base_student_1 = await utils.create_model(
                session,
                factory_lib.StudentContestFactory.build(
                    student_id=student_1.id,
                    contest_id=contest_base.id,
                    course_id=course.id,
                    tasks_done=0,
                    score=0,
                    score_no_deadline=0,
                    is_ok=False,
                    is_ok_no_deadline=False,
                ),
            )

            # student_tasks
            task_base_student_1 = await utils.create_model(
                session,
                factory_lib.StudentTaskFactory.build(
                    course_id=course.id,
                    contest_id=contest_base.id,
                    task_id=task_base.id,
                    student_id=student_1.id,
                    final_score=0,
                    best_score_before_finish=0,
                    best_score_no_deadline=0,
                    is_done=False,
                    best_score_before_finish_submission_id=None,
                    best_score_no_deadline_submission_id=None,
                ),
            )

            # submissions
            task_base_student_1_submission = await utils.create_model(
                session,
                factory_lib.SubmissionFactory.build(
                    course_id=course.id,
                    contest_id=contest_base.id,
                    task_id=task_base.id,
                    student_id=student_1.id,
                    student_task_id=task_base_student_1.id,
                    verdict='No report',
                    final_score=0,
                    score_no_deadline=0,
                    score_before_finish=0,
                    author_id=contest_base_student_1.author_id,
                    run_id=1,
                ),
            )
            task_base_student_1_submission_2 = await utils.create_model(
                session,
                factory_lib.SubmissionFactory.build(
                    course_id=course.id,
                    contest_id=contest_base.id,
                    task_id=task_base.id,
                    student_id=student_1.id,
                    student_task_id=task_base_student_1.id,
                    verdict='No report',
                    final_score=0,
                    score_no_deadline=0,
                    score_before_finish=0,
                    author_id=contest_base_student_1.author_id,
                    run_id=2,
                ),
            )

            # department
            department = await utils.create_model(
                session, factory_lib.DepartmentFactory.build()
            )
            _ = await utils.create_model(
                session,
                factory_lib.StudentDepartmentFactory.build(
                    student_id=student_1.id, department_id=department.id
                ),
            )
            _ = await utils.create_model(
                session,
                factory_lib.StudentDepartmentFactory.build(
                    student_id=student_2.id, department_id=department.id
                ),
            )

            # course_levels
            course_levels = [
                await utils.create_model(
                    session,
                    factory_lib.CourseLevelsFactory.build(
                        course_id=course.id,
                        level_name='Зачет',
                        result_update_end=datetime.datetime.now()
                        + datetime.timedelta(days=1),
                        level_info={
                            'data': [
                                {
                                    'level_ok_method': 'contests_ok',
                                    'count_method': 'percent',
                                    'ok_threshold': 50,
                                    'contest_ok_level_name': 'Допуск к зачету',
                                    'tags': ['USUAL', 'NECESSARY'],
                                },
                                {
                                    'level_ok_method': 'contests_ok',
                                    'count_method': 'absolute',
                                    'ok_threshold': 1,
                                    'contest_ok_level_name': 'Зачет',
                                    'tags': ['FINAL', 'USUAL'],
                                },
                            ]
                        },
                    ),
                ),
                await utils.create_model(
                    session,
                    factory_lib.CourseLevelsFactory.build(
                        course_id=course.id,
                        level_name='Зачет',
                        result_update_end=datetime.datetime.now()
                        + datetime.timedelta(days=1),
                        level_info={
                            'data': [
                                {
                                    'level_ok_method': 'contests_ok',
                                    'count_method': 'percent',
                                    'ok_threshold': 50,
                                    'contest_ok_level_name': 'Допуск к зачету',
                                    'tags': ['EARLY_EXAM', 'NECESSARY'],
                                },
                                {
                                    'level_ok_method': 'contests_ok',
                                    'count_method': 'absolute',
                                    'ok_threshold': 1,
                                    'contest_ok_level_name': 'Зачет',
                                    'tags': ['FINAL', 'EARLY_EXAM'],
                                },
                            ]
                        },
                    ),
                ),
            ]

            mock_make_request_to_yandex_contest_v2(
                {
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'submissions\?page=1&pageSize=100$': {
                        'json': {
                            'count': 1,
                            'submissions': [
                                {
                                    'id': 3,
                                    'authorId': 12345,
                                    'problemId': task_base.yandex_task_id,
                                    'problemAlias': task_base.alias,
                                    'verdict': 'OK',
                                },
                            ],
                        },
                    },
                    rf'^contests\/{contest_early_final.yandex_contest_id}\/'
                    rf'submissions\?page=1&pageSize=100$': {
                        'json': {
                            'count': 1,
                            'submissions': [
                                {
                                    'id': 3423,
                                    'authorId': 64876,
                                    'problemId': task_early_final.yandex_task_id,  # pylint: disable=line-too-long
                                    'problemAlias': task_early_final.alias,
                                    'verdict': 'OK',
                                }
                            ],
                        },
                    },
                    rf'^contests\/{contest_usual_final.yandex_contest_id}\/'
                    rf'submissions\?page=1&pageSize=100$': {
                        'json': {
                            'count': 2,
                            'submissions': [
                                {
                                    'id': 987,
                                    'authorId': 1234567,
                                    'problemId': task_usual_final.yandex_task_id,  # pylint: disable=line-too-long
                                    'problemAlias': task_usual_final.alias,
                                    'verdict': 'OK',
                                },
                                {
                                    'id': 657,
                                    'authorId': 32332323,
                                    'problemId': task_usual_final.yandex_task_id,  # pylint: disable=line-too-long
                                    'problemAlias': task_usual_final.alias,
                                    'verdict': 'WA',
                                },
                            ],
                        },
                    },
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'submissions\/multiple\?runIds='
                    rf'{task_base_student_1_submission.run_id}$': {
                        'json': [
                            {
                                'runId': task_base_student_1_submission.run_id,
                                'authorId': task_base_student_1_submission.author_id,  # pylint: disable=line-too-long
                                'problemId': task_base.yandex_task_id,
                                'problemAlias': task_base.alias,
                                'verdict': 'OK',
                                'participantInfo': {
                                    'login': student_1.contest_login,
                                },
                                'submissionTime': (
                                    contest_base.deadline
                                    + datetime.timedelta(days=1, seconds=1)
                                ).isoformat(),
                                'finalScore': '',
                            },
                        ],
                    },
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'submissions\/multiple\?runIds='
                    rf'{task_base_student_1_submission_2.run_id}$': {
                        'json': [
                            {
                                'runId': task_base_student_1_submission_2.run_id,  # pylint: disable=line-too-long
                                'authorId': task_base_student_1_submission_2.author_id,  # pylint: disable=line-too-long
                                'problemId': task_base.yandex_task_id,
                                'problemAlias': task_base.alias,
                                'verdict': 'OK',
                                'participantInfo': {
                                    'login': student_1.contest_login,
                                },
                                'submissionTime': (
                                    contest_base.deadline
                                    - datetime.timedelta(days=1, seconds=2)
                                ).isoformat(),
                                'finalScore': '1',
                            },
                        ],
                    },
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'submissions\/multiple\?runIds=3$': {
                        'json': [
                            {
                                'runId': 3,
                                'authorId': 12345,
                                'problemId': task_base.yandex_task_id,
                                'problemAlias': task_base.alias,
                                'verdict': 'OK',
                                'participantInfo': {
                                    'login': student_2.contest_login,
                                },
                                'submissionTime': (
                                    contest_base.deadline
                                    - datetime.timedelta(days=1, seconds=1)
                                ).isoformat(),
                                'finalScore': '',
                            },
                        ],
                    },
                    rf'^contests\/{contest_early_final.yandex_contest_id}\/'
                    rf'submissions\/multiple\?runIds=3423$': {
                        'json': [
                            {
                                'runId': 3423,
                                'authorId': 64876,
                                'problemId': task_early_final.yandex_task_id,
                                'problemAlias': task_early_final.alias,
                                'verdict': 'OK',
                                'participantInfo': {
                                    'login': student_1.contest_login,
                                },
                                'submissionTime': (
                                    contest_early_final.deadline
                                    - datetime.timedelta(days=1, seconds=1)
                                ).isoformat(),
                                'finalScore': '',
                            },
                        ],
                    },
                    rf'^contests\/{contest_usual_final.yandex_contest_id}\/'
                    rf'submissions\/multiple\?runIds=657&runIds=987$': {
                        'json': [
                            {
                                'runId': 987,
                                'authorId': 1234567,
                                'problemId': task_usual_final.yandex_task_id,
                                'problemAlias': task_usual_final.alias,
                                'verdict': 'OK',
                                'participantInfo': {
                                    'login': student_2.contest_login,
                                },
                                'submissionTime': (
                                    contest_usual_final.deadline
                                    - datetime.timedelta(days=1, seconds=1)
                                ).isoformat(),
                                'finalScore': '',
                            },
                            {
                                'runId': 657,
                                'authorId': 32332323,
                                'problemId': task_usual_final.yandex_task_id,
                                'problemAlias': task_usual_final.alias,
                                'verdict': 'WA',
                                'participantInfo': {
                                    'login': student_1.contest_login,
                                },
                                'submissionTime': (
                                    contest_usual_final.deadline
                                    - datetime.timedelta(days=1, seconds=1)
                                ).isoformat(),
                                'finalScore': '',
                            },
                        ],
                    },
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'participants\?login={student_1.contest_login}$': {
                        'json': [
                            {
                                'id': str(
                                    task_base_student_1_submission.author_id
                                )
                            }
                        ],
                    },
                    rf'^contests\/{contest_base.yandex_contest_id}\/'
                    rf'participants\?login={student_2.contest_login}$': {
                        'json': [{'id': '12345'}],
                    },
                    rf'^contests\/{contest_early_final.yandex_contest_id}\/'
                    rf'participants\?login={student_1.contest_login}$': {
                        'json': [{'id': '64876'}],
                    },
                    rf'^contests\/{contest_usual_final.yandex_contest_id}\/'
                    rf'participants\?login={student_1.contest_login}$': {
                        'json': [{'id': '32332323'}],
                    },
                    rf'^contests\/{contest_usual_final.yandex_contest_id}\/'
                    rf'participants\?login={student_2.contest_login}$': {
                        'json': [{'id': '1234567'}],
                    },
                }
            )

        # act
        await job(base_logger=loguru.logger, save_csv=False)

        # assert
        mock_bot.send_message.assert_not_called()

        assert (
            contest_base.default_final_score_evaluation_formula
            == course.default_final_score_evaluation_formula
        )
        assert (
            contest_early_final.default_final_score_evaluation_formula
            == course.default_final_score_evaluation_formula
        )
        assert (
            contest_usual_final.default_final_score_evaluation_formula
            == course.default_final_score_evaluation_formula
        )
        assert (
            task_base.final_score_evaluation_formula
            == contest_base.default_final_score_evaluation_formula
        )
        assert (
            task_early_final.final_score_evaluation_formula
            == contest_early_final.default_final_score_evaluation_formula
        )
        assert (
            task_usual_final.final_score_evaluation_formula
            == contest_usual_final.default_final_score_evaluation_formula
        )

        async with create_async_session(expire_on_commit=False) as session:
            submission_1 = await submission_utils.get_submission(
                session, task_base_student_1_submission.run_id
            )
            assert submission_1 is not None
            assert submission_1.final_score == task_base.score_max / 2
            assert submission_1.score_no_deadline == task_base.score_max
            assert submission_1.score_before_finish == 0

            submission_1_2 = await submission_utils.get_submission(
                session, task_base_student_1_submission_2.run_id
            )
            assert submission_1_2 is not None
            assert submission_1_2.final_score == 1
            assert submission_1_2.score_no_deadline == 1
            assert submission_1_2.score_before_finish == 1

            submission_2 = await submission_utils.get_submission(session, 3)
            assert submission_2 is not None
            assert submission_2.final_score == task_base.score_max
            assert submission_2.score_no_deadline == task_base.score_max
            assert submission_2.score_before_finish == task_base.score_max

            submission_3 = await submission_utils.get_submission(session, 3423)
            assert submission_3 is not None
            assert submission_3.final_score == task_early_final.score_max
            assert submission_3.score_no_deadline == task_early_final.score_max
            assert (
                submission_3.score_before_finish == task_early_final.score_max
            )

            submission_4 = await submission_utils.get_submission(session, 987)
            assert submission_4 is not None
            assert submission_4.final_score == task_usual_final.score_max
            assert submission_4.score_no_deadline == task_usual_final.score_max
            assert (
                submission_4.score_before_finish == task_usual_final.score_max
            )

            student_1_task_base = await task_utils.get_student_task_relation(
                session, student_1.id, task_base.id
            )
            assert student_1_task_base is not None
            assert student_1_task_base.final_score == task_base.score_max / 2
            assert (
                student_1_task_base.best_score_no_deadline
                == task_base.score_max
            )
            assert student_1_task_base.best_score_before_finish == 1
            assert not student_1_task_base.is_done
            assert (
                student_1_task_base.best_score_before_finish_submission_id
                == task_base_student_1_submission_2.id
            )
            assert (
                student_1_task_base.best_score_no_deadline_submission_id
                == task_base_student_1_submission.id
            )

            student_2_task_base = await task_utils.get_student_task_relation(
                session, student_2.id, task_base.id
            )
            assert student_2_task_base is not None
            assert student_2_task_base.final_score == task_base.score_max
            assert (
                student_2_task_base.best_score_no_deadline
                == task_base.score_max
            )
            assert (
                student_2_task_base.best_score_before_finish
                == task_base.score_max
            )
            assert student_2_task_base.is_done
            assert (
                student_2_task_base.best_score_before_finish_submission_id
                == submission_2.id
            )
            assert (
                student_2_task_base.best_score_no_deadline_submission_id
                == submission_2.id
            )

            student_1_task_early_final = (
                await task_utils.get_student_task_relation(
                    session, student_1.id, task_early_final.id
                )
            )
            assert student_1_task_early_final is not None
            assert (
                student_1_task_early_final.final_score
                == task_early_final.score_max
            )
            assert (
                student_1_task_early_final.best_score_no_deadline
                == task_early_final.score_max
            )
            assert (
                student_1_task_early_final.best_score_before_finish
                == task_early_final.score_max
            )
            assert student_1_task_early_final.is_done
            assert (
                student_1_task_early_final.best_score_before_finish_submission_id  # pylint: disable=line-too-long
                == submission_3.id
            )
            assert (
                student_1_task_early_final.best_score_no_deadline_submission_id
                == submission_3.id
            )

            student_2_task_usual_final = (
                await task_utils.get_student_task_relation(
                    session, student_2.id, task_usual_final.id
                )
            )
            assert student_2_task_usual_final is not None
            assert (
                student_2_task_usual_final.final_score
                == task_usual_final.score_max
            )
            assert (
                student_2_task_usual_final.best_score_no_deadline
                == task_usual_final.score_max
            )
            assert (
                student_2_task_usual_final.best_score_before_finish
                == task_usual_final.score_max
            )
            assert student_2_task_usual_final.is_done
            assert (
                student_2_task_usual_final.best_score_before_finish_submission_id  # pylint: disable=line-too-long
                == submission_4.id
            )
            assert (
                student_2_task_usual_final.best_score_no_deadline_submission_id  # pylint: disable=line-too-long
                == submission_4.id
            )

            # student_contest
            student_1_contest_base = (
                await contest_utils.get_student_contest_relation(
                    session, student_1.id, contest_base.id
                )
            )
            assert student_1_contest_base is not None
            assert student_1_contest_base.score == task_base.score_max / 2
            assert (
                student_1_contest_base.score_no_deadline == task_base.score_max
            )
            assert student_1_contest_base.tasks_done == 0
            assert not student_1_contest_base.is_ok
            assert student_1_contest_base.is_ok_no_deadline

            student_2_contest_base = (
                await contest_utils.get_student_contest_relation(
                    session, student_2.id, contest_base.id
                )
            )
            assert student_2_contest_base is not None
            assert student_2_contest_base.score == task_base.score_max
            assert (
                student_2_contest_base.score_no_deadline == task_base.score_max
            )
            assert (
                student_2_contest_base.tasks_done == contest_base.tasks_count
            )
            assert student_2_contest_base.is_ok
            assert student_2_contest_base.is_ok_no_deadline

            student_1_contest_early_final = (
                await contest_utils.get_student_contest_relation(
                    session, student_1.id, contest_early_final.id
                )
            )
            assert student_1_contest_early_final is not None
            assert (
                student_1_contest_early_final.score
                == task_early_final.score_max
            )
            assert (
                student_1_contest_early_final.score_no_deadline
                == task_early_final.score_max
            )
            assert (
                student_1_contest_early_final.tasks_done
                == contest_early_final.tasks_count
            )
            assert student_1_contest_early_final.is_ok
            assert student_1_contest_early_final.is_ok_no_deadline

            student_2_contest_usual_final = (
                await contest_utils.get_student_contest_relation(
                    session, student_2.id, contest_usual_final.id
                )
            )
            assert student_2_contest_usual_final is not None
            assert (
                student_2_contest_usual_final.score
                == task_usual_final.score_max
            )
            assert (
                student_2_contest_usual_final.score_no_deadline
                == task_usual_final.score_max
            )
            assert (
                student_2_contest_usual_final.tasks_done
                == contest_usual_final.tasks_count
            )
            assert student_2_contest_usual_final.is_ok
            assert student_2_contest_usual_final.is_ok_no_deadline

            student_1_contest_base_levels = [
                await contest_utils.get_or_create_student_contest_level(
                    session, student_1.id, course.id, contest_base.id, level.id
                )
                for level in contest_base_levels
            ]
            assert list(
                map(lambda x: x.is_ok, student_1_contest_base_levels)
            ) == [False, True, True]

            student_2_contest_base_levels = [
                await contest_utils.get_or_create_student_contest_level(
                    session, student_2.id, course.id, contest_base.id, level.id
                )
                for level in contest_base_levels
            ]
            assert list(
                map(lambda x: x.is_ok, student_2_contest_base_levels)
            ) == [True, True, True]

            student_1_contest_early_final_levels = [
                await contest_utils.get_or_create_student_contest_level(
                    session,
                    student_1.id,
                    course.id,
                    contest_early_final.id,
                    level.id,
                )
                for level in contest_early_final_levels
            ]
            assert list(
                map(lambda x: x.is_ok, student_1_contest_early_final_levels)
            ) == [True]

            student_2_contest_usual_final_levels = [
                await contest_utils.get_or_create_student_contest_level(
                    session,
                    student_2.id,
                    course.id,
                    contest_usual_final.id,
                    level.id,
                )
                for level in contest_usual_final_levels
            ]
            assert list(
                map(lambda x: x.is_ok, student_2_contest_usual_final_levels)
            ) == [True]

            # student_course
            student_1_course_levels = [
                await course_utils.get_or_create_student_course_level(
                    session, student_1.id, course.id, course_level.id
                )
                for course_level in course_levels
            ]
            assert list(map(lambda x: x.is_ok, student_1_course_levels)) == [
                False,
                True,
            ]

            student_2_course_levels = [
                await course_utils.get_or_create_student_course_level(
                    session, student_2.id, course.id, course_level.id
                )
                for course_level in course_levels
            ]
            assert list(map(lambda x: x.is_ok, student_2_course_levels)) == [
                True,
                False,
            ]

            # course
            student_1_course_model = await course_utils.get_student_course(
                session, student_1.id, course.id
            )
            assert student_1_course_model is not None
            assert (
                student_1_course_model.score_no_deadline
                == task_base.score_max + task_early_final.score_max
            )
            assert (
                student_1_course_model.score
                == task_base.score_max / 2 + task_early_final.score_max
            )
            assert student_1_course_model.is_ok

            student_2_course_model = await course_utils.get_student_course(
                session, student_2.id, course.id
            )
            assert student_2_course_model is not None
            assert (
                student_2_course_model.score
                == task_base.score_max + task_usual_final.score_max
            )
            assert student_2_course_model.is_ok
