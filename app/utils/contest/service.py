# pylint: disable=too-many-lines

from datetime import datetime, timedelta

import httpx
import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contest, Course, Student, StudentContest
from app.m3tqdm import tqdm
from app.schemas import (
    ContestSubmission,
    ContestSubmissionFull,
    YandexContestInfo,
)
from app.schemas import contest as contest_schemas
from app.utils.common.datetime_utils import get_datetime_msk_tz
from app.utils.yandex_request import make_request_to_yandex_contest_api

from ...database import models
from .database import (
    add_student_contest_relation,
    get_student_contest_relation,
)


async def add_student_to_contest(
    session: AsyncSession,
    contest: Contest,
    student: Student,
    logger: 'loguru.Logger',
) -> tuple[bool, str | None]:
    """
    Add student to Yandex contest.
    """

    response = await make_request_to_yandex_contest_api(
        f'contests/{contest.yandex_contest_id}/participants'
        f'?login={student.contest_login}',
        logger=logger,
        method='POST',
    )

    match response.status_code:
        case 404:
            message = f'Contest {contest.yandex_contest_id} not found'
            return False, message
        case 409:
            logger.warning(
                'Student "{}" already registered on contest "{}"',
                student.contest_login,
                contest.yandex_contest_id,
            )
        case 401:
            message = 'Yandex API key is invalid. Please check it in .env file'
            return False, message
        case 403:
            message = (
                'Yandex API key does not have access to the contest '
                f'"{contest.yandex_contest_id}"'
            )
            return False, message
        case 201:
            logger.info(
                'Student "{}" successfully added to contest "{}"',
                student.contest_login,
                contest.yandex_contest_id,
            )
        case 200:
            logger.warning(
                'Student "{}" already registered on contest "{}" (code 200)',
                student.contest_login,
                contest.yandex_contest_id,
            )
        case _:
            message = (
                f'Unknown error. Status code: {response.status_code}. '
                f'Text: {response.text}'
            )
            return False, message

    await add_student_contest_relation(
        session, student.id, contest.id, contest.course_id, int(response.text)
    )
    logger.info(
        'Student "{}" successfully added to contest "{}" in database',
        student.contest_login,
        contest.yandex_contest_id,
    )
    return True, None


async def get_author_id(
    login: str,
    yandex_contest_id: int,
    logger: 'loguru.Logger',
) -> int:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/participants' f'?login={login}',
        logger=logger,
        method='POST',
    )
    return int(response.text)


async def get_contest_info(
    yandex_contest_id: int,
    logger: 'loguru.Logger',
) -> YandexContestInfo:
    response_contest = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}',
        logger=logger,
    )
    data = response_contest.json()
    deadline = get_datetime_msk_tz(data['startTime']) + timedelta(
        seconds=data['duration']
    )
    duration = data['duration']
    resopnse_task = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/problems',
        logger=logger,
    )
    data = resopnse_task.json()
    tasks_count = len(data['problems'])
    return YandexContestInfo(
        deadline=deadline,
        tasks_count=tasks_count,
        duration=duration,
        tasks=[
            contest_schemas.Task(
                yandex_task_id=problem['id'],
                name=problem['name'],
                alias=problem['alias'],
            )
            for problem in data['problems']
        ],
    )


async def get_or_create_student_contest(
    session: AsyncSession,
    student: Student,
    contest: Contest,
    course: Course,
    logger: 'loguru.Logger',
) -> StudentContest:
    sc = await get_student_contest_relation(session, student.id, contest.id)
    if sc is None:
        sc = await add_student_contest_relation(
            session,
            student.id,
            contest.id,
            course.id,
            await get_author_id(
                student.contest_login, contest.yandex_contest_id, logger=logger
            ),
        )
    return sc


async def get_new_submissions(
    contest: Contest,
    last_updated_submission: int,
    logger: 'loguru.Logger',
) -> list[ContestSubmissionFull]:
    url = (
        f'contests/{contest.yandex_contest_id}/submissions'
        f'?page={{}}&pageSize={{}}'
    )
    page = 1
    page_size = 100
    result_dict: dict[int, ContestSubmission] = {}

    response = await make_request_to_yandex_contest_api(
        url.format(page, page_size), logger=logger
    )
    data = response.json()
    all_submissions_count = data['count']
    logger.info(
        'Contest {} has {} submissions',
        contest.yandex_contest_id,
        all_submissions_count,
    )

    while len(result_dict) != all_submissions_count:
        new_values = dict(
            map(
                lambda submission: (
                    int(submission['id']),
                    ContestSubmission(**submission),
                ),
                filter(
                    lambda submission: not last_updated_submission
                    or int(submission['id']) > last_updated_submission,
                    data['submissions'],
                ),
            )
        )
        result_dict.update(new_values)
        if len(new_values) < len(data['submissions']):
            break
        if len(result_dict) == all_submissions_count:
            break
        page += 1
        response = await make_request_to_yandex_contest_api(
            url.format(page, page_size), logger=logger
        )
        data = response.json()
    return await make_full_submissions(
        result_dict,
        contest,
        logger=logger,
    )


async def make_full_submissions(
    submissions: dict[int, ContestSubmission],
    contest: Contest,
    logger: 'loguru.Logger',
) -> list[ContestSubmissionFull]:
    url = f'contests/{contest.yandex_contest_id}/submissions/multiple?'
    batch_size = 100
    results: list[ContestSubmissionFull] = []
    submission_values = sorted(
        list(
            submissions.values(),
        ),
        key=lambda x: x.id,
    )
    logger.info(
        'Getting submissions for contest "{}" for {} submissions',
        contest.yandex_contest_id,
        len(submission_values),
    )
    async for i in tqdm(
        range(0, len(submission_values), batch_size),
        name='make_full_submissions',
        total=(len(submission_values) + batch_size - 1) // batch_size,
    ):
        batch_url = url + '&'.join(
            map(
                lambda run_id: f'runIds={run_id}',
                [
                    submission_value.id
                    for submission_value in submission_values[
                        i : i + batch_size
                    ]
                ],
            )
        )
        first_id, last_id = (
            submission_values[i].id,
            submission_values[i + batch_size].id
            if i + batch_size < len(submission_values)
            else submission_values[-1].id,
        )
        logger.info(
            'Getting submissions ids {}-{} (index {}-{})',
            first_id,
            last_id,
            i,
            i + batch_size
            if i + batch_size < len(submission_values)
            else len(submission_values) - 1,
        )
        try:
            response = await make_request_to_yandex_contest_api(
                batch_url, timeout=60, retry_count=5, logger=logger
            )
        except httpx.ReadTimeout:
            logger.error(
                'Timeout error for submissions ids {}-{} (index {}-{})',
                first_id,
                last_id,
                i,
                i + batch_size
                if i + batch_size < len(submission_values)
                else len(submission_values) - 1,
            )
            continue
        if response.status_code != 200:
            logger.error(
                'Error while getting submissions {}-{} (index {}-{}). '
                'Status code: {}. Response: {}',
                first_id,
                last_id,
                i,
                i + batch_size
                if i + batch_size < len(submission_values)
                else len(submission_values) - 1,
                response.status_code,
                response.text,
            )
            continue
        results.extend(
            ContestSubmissionFull(
                id=submission['runId'],
                authorId=submissions[submission['runId']].authorId,
                problemId=submission['problemId'],
                problemAlias=submission['problemAlias'],
                verdict=submission['verdict'],
                login=submission['participantInfo']['login'],
                timeFromStart=submission['timeFromStart'],
                submissionTime=datetime.fromisoformat(
                    submission['submissionTime']
                ).replace(tzinfo=None),
                finalScore=(
                    float(submission['finalScore'])
                    if isinstance(submission['finalScore'], str)
                    and submission['finalScore']
                    and float(submission['finalScore'])
                    else 0
                ),
            )
            for submission in response.json()
        )
    return results


async def get_submission_from_yandex(
    contest: Contest,
    submission: models.Submission,
    logger: 'loguru.Logger',
) -> ContestSubmissionFull:
    return (
        await make_full_submissions(
            {
                submission.run_id: ContestSubmission(
                    id=submission.run_id,
                    authorId=submission.author_id,
                    problemId='',
                    problemAlias='',
                    verdict='',
                )
            },
            contest,
            logger,
        )
    )[0]
