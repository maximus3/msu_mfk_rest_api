import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contest, Student
from app.schemas import (
    ContestProblem,
    ContestSubmission,
    ContestSubmissionFull,
)
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
        session, student.id, contest.id, contest.course_id
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
    result_list: list[ContestSubmission],
) -> None:
    result_list.extend(
        map(
            lambda submission: ContestSubmission(**submission),
            filter(lambda submission: submission['verdict'] == 'OK', data),
        )
    )


async def extend_submissions(
    submissions: list[ContestSubmission],
    yandex_contest_id: int,
) -> list[ContestSubmissionFull]:
    logger = logging.getLogger(__name__)
    url = f'contests/{yandex_contest_id}/submissions/multiple?'
    batch_size = 100
    results: list[ContestSubmissionFull] = []
    for i in range(0, len(submissions), batch_size):
        batch_url = url + '&'.join(
            map(
                lambda run_id: f'runIds={run_id}',
                [
                    submission.id
                    for submission in submissions[i : i + batch_size]
                ],
            )
        )
        logger.info('Getting submissions %s-%s', i, i + batch_size)
        response = await make_request_to_yandex_contest_api(
            batch_url, timeout=30
        )
        results.extend(
            ContestSubmissionFull(
                id=submission['runId'],
                authorId=submission['participantInfo']['id'],
                problemId=submission['problemId'],
                problemAlias=submission['problemAlias'],
                verdict=submission['verdict'],
                login=submission['participantInfo']['login'],
                finalScore=float(submission['finalScore'])
                if isinstance(submission['finalScore'], str)
                and submission['finalScore']
                else 1,
            )
            for submission in response.json()
        )
    return results


async def filter_best_submissions_only(
    submissions: list[ContestSubmissionFull],
) -> list[ContestSubmissionFull]:
    result = []
    for login in set(map(lambda submission: submission.login, submissions)):
        for task_id in set(
            map(lambda submission: submission.problemId, submissions)
        ):
            result.extend(
                sorted(
                    filter(
                        lambda submission: (
                            submission.login
                            == login  # pylint: disable=cell-var-from-loop
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
    yandex_contest_id: int,
) -> list[ContestSubmissionFull]:
    logger = logging.getLogger(__name__)
    url = f'contests/{yandex_contest_id}/submissions?page={{}}&pageSize={{}}'
    page = 1
    page_size = 100
    result_list: list[ContestSubmission] = []

    response = await make_request_to_yandex_contest_api(
        url.format(page, page_size)
    )
    data = response.json()
    count = data['count']
    count_done = 0
    logger.info('Contest %s has %s submissions', yandex_contest_id, count)
    while count_done < count:
        await _add_results(data['submissions'], result_list)
        count_done += len(data['submissions'])
        if count_done == count:
            break
        page += 1
        response = await make_request_to_yandex_contest_api(
            url.format(page, page_size)
        )
        data = response.json()
    return await filter_best_submissions_only(
        await extend_submissions(result_list, yandex_contest_id)
    )
