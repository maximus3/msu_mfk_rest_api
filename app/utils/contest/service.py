# pylint: disable=too-many-lines

from datetime import datetime, timedelta

import httpx
import loguru
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contest, Course, Student, StudentContest
from app.m3tqdm import tqdm
from app.schemas import (
    ContestProblem,
    ContestSubmission,
    ContestSubmissionFull,
    YandexContestInfo,
)
from app.utils.common import get_datetime_msk_tz
from app.utils.scheduler import write_sql_tqdm
from app.utils.yandex_request import make_request_to_yandex_contest_api

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
            message = f'Unknown error. Status code: {response.status_code}'
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


async def get_problems(
    yandex_contest_id: int,
    logger: 'loguru.Logger',
) -> list[ContestProblem]:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/problems',
        logger=logger,
    )
    return sorted(
        [ContestProblem(**problem) for problem in response.json()['problems']],
        key=lambda problem: problem.alias,
    )


async def get_participants_login_to_id(
    yandex_contest_id: int,
    logger: 'loguru.Logger',
) -> dict[str, int]:
    response = await make_request_to_yandex_contest_api(
        f'contests/{yandex_contest_id}/participants',
        logger=logger,
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
    logger: 'loguru.Logger',
    zero_is_ok: bool = False,
) -> tuple[list[ContestSubmissionFull], bool]:
    ok_authors_ids = ok_authors_ids or set()
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
        'Getting submissions for contest "{}" '
        'with {} not ok authors submissions',
        contest.yandex_contest_id,
        len(submission_values),
    )
    async for i in tqdm(
        range(0, len(submission_values), batch_size),
        name='extend_submissions',
        total=(len(submission_values) + batch_size - 1) // batch_size,
        sql_write_func=write_sql_tqdm,
    ):
        batch_url = url + '&'.join(
            map(
                lambda run_id: f'runIds={run_id}',
                [
                    submission.id
                    for submission in submission_values[i : i + batch_size]
                ],
            )
        )
        logger.info('Getting submissions {}-{}', i, i + batch_size)
        try:
            response = await make_request_to_yandex_contest_api(
                batch_url, timeout=60, retry_count=5, logger=logger
            )
        except httpx.ReadTimeout:
            logger.error('Timeout error')
            is_all_results = False
            continue
        if response.status_code != 200:
            logger.error(
                'Error while getting submissions {}-{}. '
                'Status code: {}. Response: {}',
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
                    else (
                        1
                        if zero_is_ok and submission['verdict'] == 'OK'
                        else 0
                    )
                ),
                finalScore=(
                    float(submission['finalScore'])
                    if isinstance(submission['finalScore'], str)
                    and submission['finalScore']
                    and float(submission['finalScore'])
                    else (
                        1
                        if zero_is_ok and submission['verdict'] == 'OK'
                        else 0
                    )
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
                    else (
                        0.5
                        if zero_is_ok and submission['verdict'] == 'OK'
                        else 0
                    )
                ),
            )
            for submission in response.json()
        )
    return results, is_all_results


async def filter_best_submissions_only(
    submissions: list[ContestSubmissionFull],
    sort_by_final: bool = True,
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
                    key=lambda submission: submission.finalScore
                    if sort_by_final
                    else submission.noDeadlineScore,
                    reverse=True,
                )[:1]
            )
    return result


async def get_best_submissions(
    contest: Contest,
    logger: 'loguru.Logger',
    zero_is_ok: bool = False,
    ok_authors_ids: set[int] | None = None,
) -> tuple[list[ContestSubmissionFull], bool]:
    ok_authors_ids = ok_authors_ids or set()
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
    count = data['count']
    count_done = 0
    logger.info(
        'Contest {} has {} submissions', contest.yandex_contest_id, count
    )
    while count_done < count:
        await _add_results(data['submissions'], result_dict)
        count_done += len(data['submissions'])
        if count_done == count:
            break
        page += 1
        response = await make_request_to_yandex_contest_api(
            url.format(page, page_size), logger=logger
        )
        data = response.json()
    extended_results, is_all_results = await extend_submissions(
        result_dict,
        contest,
        ok_authors_ids,
        logger=logger,
        zero_is_ok=zero_is_ok,
    )
    return await filter_best_submissions_only(extended_results), is_all_results


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
    )


async def get_student_best_submissions(
    contest: Contest,
    student: Student,
    student_contest: StudentContest,
    logger: 'loguru.Logger',
    zero_is_ok: bool = False,
) -> list[ContestSubmissionFull]:
    url = (
        f'contests/{contest.yandex_contest_id}/participants/'
        f'{student_contest.author_id}/stats'
    )

    response = await make_request_to_yandex_contest_api(url, logger=logger)
    if response.status_code != 200:
        logger.error(
            'Error while getting results for student {} (id={})'
            'Status code: {}. Response: {}',
            student.contest_login,
            student_contest.author_id,
            response.status_code,
            response.text,
        )
    data = response.json()
    runs = data['runs']

    logger.info(
        'Got {} submissions for contest "{}" with author {} (id={})',
        len(runs),
        contest.yandex_contest_id,
        student.contest_login,
        student_contest.author_id,
    )

    results = [
        ContestSubmissionFull(
            id=submission['runId'],
            authorId=data['id'],
            problemId=submission['problemId'],
            problemAlias=submission['problemAlias'],
            verdict=submission['verdict'],
            login=data['login'],
            timeFromStart=submission['timeFromStart'],
            noDeadlineScore=(
                float(submission['finalScore'])
                if isinstance(submission['finalScore'], str)
                and submission['finalScore']
                and float(submission['finalScore'])
                else (1 if zero_is_ok and submission['verdict'] == 'OK' else 0)
            ),
            finalScore=(
                float(submission['finalScore'])
                if isinstance(submission['finalScore'], str)
                and submission['finalScore']
                and float(submission['finalScore'])
                else (1 if zero_is_ok and submission['verdict'] == 'OK' else 0)
            )
            if datetime.fromisoformat(submission['submissionTime']).replace(
                tzinfo=None
            )
            <= contest.deadline
            else 0,
        )
        for submission in runs
    ]

    return await filter_best_submissions_only(results, sort_by_final=False)


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
                submission_values[i : i + batch_size],
            )
        )
        first_id, last_id = (
            submission_values[i],
            submission_values[i + batch_size]
            if i + batch_size < len(submission_values)
            else submission_values[-1],
        )
        logger.info(
            'Getting submissions ids {}-{} (index {}-{})',
            first_id,
            last_id,
            i,
            i + batch_size,
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
                i + batch_size,
            )
            continue
        if response.status_code != 200:
            logger.error(
                'Error while getting submissions {}-{} (index {}-{}). '
                'Status code: {}. Response: {}',
                first_id,
                last_id,
                i,
                i + batch_size,
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
                    submission['submissionTime'].replace(tzinfo=None)
                ),
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
