# pylint: disable=too-many-lines

import logging
from datetime import datetime, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contest, Student
from app.schemas import (
    ContestProblem,
    ContestSubmission,
    ContestSubmissionFull,
    YandexContestInfo,
)
from app.utils.common import get_datetime_msk_tz
from app.utils.yandex_request import make_request_to_yandex_contest_api

from .database import add_student_contest_relation


async def add_student_to_contest(
    session: AsyncSession,
    contest: Contest,
    student: Student,
) -> tuple[bool, str | None]:
    """
    Add student to Yandex contest.
    """
    logger = logging.getLogger(__name__)

    response = await make_request_to_yandex_contest_api(
        f'contests/{contest.yandex_contest_id}/participants'
        f'?login={student.contest_login}',
        method='POST',
    )

    match response.status_code:
        case 404:
            message = f'Contest {contest.yandex_contest_id} not found'
            return False, message
        case 409:
            logger.warning(
                'Student "%s" already registered on contest "%s"',
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
                'Student "%s" successfully added to contest "%s"',
                student.contest_login,
                contest.yandex_contest_id,
            )
        case 200:
            logger.warning(
                'Student "%s" already registered on contest "%s" (code 200)',
                student.contest_login,
                contest.yandex_contest_id,
            )
        case _:
            message = f'Unknown error. Status code: {response.status_code}'
            return False, message

    await add_student_contest_relation(
        session, student.id, contest.id, contest.course_id, int(response.text)
    )
    logger.info(
        'Student "%s" successfully added to contest "%s" in database',
        student.contest_login,
        contest.yandex_contest_id,
    )
    return True, None


async def get_problems(
    yandex_contest_id: int,
) -> list[ContestProblem]:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/problems'
    )
    return sorted(
        [ContestProblem(**problem) for problem in response.json()['problems']],
        key=lambda problem: problem.alias,
    )


async def get_participants_login_to_id(
    yandex_contest_id: int,
) -> dict[str, int]:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/participants'
    )
    return {
        participant['login']: participant['id']
        for participant in response.json()
    }


async def _add_results(
    data: list[dict[str, str]],
    result_list: dict[int, ContestSubmission],
) -> None:
    result_list.update(
        dict(
            map(
                lambda submission: (
                    int(submission['id']),
                    ContestSubmission(**submission),
                ),
                filter(lambda submission: submission['verdict'] == 'OK', data),
            )
        )
    )


async def extend_submissions(
    submissions: dict[int, ContestSubmission],
    contest: Contest,
    ok_authors_ids: set[int],
    zero_is_ok: bool = False,
) -> tuple[list[ContestSubmissionFull], bool]:
    ok_authors_ids = ok_authors_ids or set()
    logger = logging.getLogger(__name__)
    url = f'contests/{contest.yandex_contest_id}/submissions/multiple?'
    batch_size = 100
    results: list[ContestSubmissionFull] = []
    is_all_results = True
    submission_values = list(
        filter(
            lambda submission: submission.authorId not in ok_authors_ids,
            submissions.values(),
        )
    )
    logger.info(
        'Getting submissions for contest "%s" '
        'with %s not ok authors submissions',
        contest.yandex_contest_id,
        len(submission_values),
    )
    for i in range(0, len(submission_values), batch_size):
        batch_url = url + '&'.join(
            map(
                lambda run_id: f'runIds={run_id}',
                [
                    submission.id
                    for submission in submission_values[i : i + batch_size]
                ],
            )
        )
        logger.info('Getting submissions %s-%s', i, i + batch_size)
        try:
            response = await make_request_to_yandex_contest_api(
                batch_url, timeout=60, retry_count=5
            )
        except httpx.ReadTimeout:
            logger.error('Timeout error')
            is_all_results = False
            continue
        if response.status_code != 200:
            logger.error(
                'Error while getting submissions %s-%s. Status code: %s. Response: %s',
                i,
                i + batch_size,
                response.status_code,
                response.text,
            )
            is_all_results = False
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
                noDeadlineScore=(
                    float(submission['finalScore'])
                    if isinstance(submission['finalScore'], str)
                    and submission['finalScore']
                    and float(submission['finalScore'])
                    else (1 if zero_is_ok else 0)
                ),
                finalScore=(
                    float(submission['finalScore'])
                    if isinstance(submission['finalScore'], str)
                    and submission['finalScore']
                    and float(submission['finalScore'])
                    else (1 if zero_is_ok else 0)
                )
                if datetime.fromisoformat(
                    submission['submissionTime']
                ).replace(tzinfo=None)
                <= contest.deadline
                else (
                    float(submission['finalScore']) / 2
                    if isinstance(submission['finalScore'], str)
                    and submission['finalScore']
                    and float(submission['finalScore'])
                    else (0.5 if zero_is_ok else 0)
                ),
            )
            for submission in response.json()
        )
    return results, is_all_results


async def filter_best_submissions_only(
    submissions: list[ContestSubmissionFull],
) -> list[ContestSubmissionFull]:
    result = []
    for author_id in set(
        map(lambda submission: submission.authorId, submissions)
    ):
        for task_id in set(
            map(lambda submission: submission.problemId, submissions)
        ):
            if task_id in [
                '5897533/2021_10_05/6OX0YJhjMw',
                '5897533/2021_10_13/4aAHf8v2kd',
            ]:  # TODO: ФИО and  Факультет tasks
                continue
            result.extend(
                sorted(
                    filter(
                        lambda submission: (
                            submission.authorId
                            == author_id  # pylint: disable=cell-var-from-loop
                            and submission.problemId
                            == task_id  # pylint: disable=cell-var-from-loop
                        ),
                        submissions,
                    ),
                    key=lambda submission: submission.finalScore,
                    reverse=True,
                )[:1]
            )
    return result


async def get_best_submissions(
    contest: Contest,
    zero_is_ok: bool = False,
    ok_authors_ids: set[int] | None = None,
) -> tuple[list[ContestSubmissionFull], bool]:
    ok_authors_ids = ok_authors_ids or set()
    logger = logging.getLogger(__name__)
    url = (
        f'contests/{contest.yandex_contest_id}/submissions'
        f'?page={{}}&pageSize={{}}'
    )
    page = 1
    page_size = 100
    result_dict: dict[int, ContestSubmission] = {}

    response = await make_request_to_yandex_contest_api(
        url.format(page, page_size)
    )
    data = response.json()
    count = data['count']
    count_done = 0
    logger.info(
        'Contest %s has %s submissions', contest.yandex_contest_id, count
    )
    while count_done < count:
        await _add_results(data['submissions'], result_dict)
        count_done += len(data['submissions'])
        if count_done == count:
            break
        page += 1
        response = await make_request_to_yandex_contest_api(
            url.format(page, page_size)
        )
        data = response.json()
    extended_results, is_all_results = await extend_submissions(
        result_dict, contest, ok_authors_ids, zero_is_ok
    )
    return await filter_best_submissions_only(extended_results), is_all_results


async def get_author_id(
    login: str,
    yandex_contest_id: int,
) -> int:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/participants' f'?login={login}',
        method='POST',
    )
    return int(response.text)


async def get_contest_info(
    yandex_contest_id: int,
) -> YandexContestInfo:
    response_contest = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}'
    )
    data = response_contest.json()
    deadline = get_datetime_msk_tz(data['startTime']) + timedelta(
        seconds=data['duration']
    )
    duration = data['duration']
    resopnse_task = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/problems'
    )
    data = resopnse_task.json()
    tasks_count = len(data['problems'])
    return YandexContestInfo(
        deadline=deadline,
        tasks_count=tasks_count,
        duration=duration,
    )
