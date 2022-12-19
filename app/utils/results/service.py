import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Course, Student, StudentCourse
from app.schemas import ContestResults, CourseResults
from app.utils.common import get_datetime_msk_tz
from app.utils.contest import get_contests_with_relations


async def get_student_course_results(
    student: Student,
    course: Course,
    student_course: StudentCourse,
    session: AsyncSession,
) -> CourseResults:
    logger = logging.getLogger(__name__)

    contests = []
    course_score_max = 0

    for contest, student_contest in sorted(
        await get_contests_with_relations(
            session,
            course.id,
            student.id,
        ),
        key=lambda x: x[0].lecture,
    ):
        course_score_max += contest.score_max

        contests.append(
            ContestResults(
                link=contest.link,
                tasks_count=contest.tasks_count,
                score_max=contest.score_max,
                levels_count=contest.levels['count'] if contest.levels else 0,
                levels=sorted(
                    contest.levels['levels'],
                    key=lambda level: level['score_need'],
                )
                if contest.levels
                else [],
                levels_ok=[
                    (student_contest.score or 0) >= level['score_need']
                    for level in sorted(
                        contest.levels['levels'],
                        key=lambda level: level['score_need'],
                    )
                ]
                if contest.levels
                else [],
                lecture=contest.lecture,
                tasks_done=student_contest.tasks_done,
                score=student_contest.score,
                is_ok=student_contest.is_ok,
                is_necessary=contest.is_necessary,
                updated_at=get_datetime_msk_tz(
                    student_contest.dt_updated
                ).strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
                deadline=get_datetime_msk_tz(contest.deadline).strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
            )
        )

    if course.ok_method == 'contests_ok':
        perc_ok = student_course.contests_ok_percent
    elif course.ok_method == 'score_sum':
        perc_ok = student_course.score_percent
    else:
        logger.error('Unknown ok_method: %s', course.ok_method)
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    tmp = {
        'dl_autumn_2022': 'Зачет пройдет 21 декабря и будет состоять из онлайн-задания на 1,5 часа в системе Яндекс.Контест. Ссылка на задание появится в Telegram-канале курса.\nНО для получения зачета вам необходимо набрать не менее 7 баллов за домашние задания по курсу.',
        'da_autumn_2022': 'Зачет пройдет 21 декабря и будет состоять из онлайн-задания на 1,5 часа в системе Яндекс.Контест. Ссылка на задание появится в Telegram-канале курса.\nНО для получения зачета вам необходимо решить не менее 50% задач из каждого домашнего задания к лекциям 2-10.',
        'ml_autumn_2022': 'Зачет пройдет 21 декабря и будет состоять из онлайн-задания на 1,5 часа в системе Яндекс.Контест. Ссылка на задание появится в Telegram-канале курса.\nНО для получения зачета вам необходимо решить все домашние задания по курсу. Домашнее задание считается решенным, если выполнено количество задач, определенное для получения зачета (например, для зачета нужно было набрать 12 баллов, но студент выполнил все задания после дедлайна, получил 6 баллов, этого достаточно, чтобы засчитать данное домашнее задание для допуска к зачету).',
    }

    return CourseResults(
        name=course.name,
        contests=contests,
        score_sum=student_course.score,
        score_max=course_score_max,
        is_ok=student_course.is_ok,
        perc_ok=int(perc_ok),
        str_need=f'Вы набрали необходимое количество баллов для зачета по курсу "{course.name}". Обратите внимание, что для получения зачета, вы должны были зарегистрироваться на курс через ЛК до 18 декабря.  Проверьте, что ФИО, которое вы указывали при регистрации через чат-бота, полностью совпадает с ФИО в ЛК https://lk.msu.ru/. В случае обнаружения неточностей, напишите нам с помощью этого чат-бота. О проставлении зачетов мы сообщим в официальном Telegram-канале курса.' if student_course.is_ok else tmp[course.short_name],
    )


async def update_student_course_results(  # pylint: disable=too-many-statements
    student: Student,
    course: Course,
    student_course: StudentCourse,
    session: AsyncSession,
) -> None:
    logger = logging.getLogger(__name__)

    course_score_sum = 0
    course_score_max = 0
    necessary_contests_results = []

    for contest, student_contest in await get_contests_with_relations(
        session,
        course.id,
        student.id,
    ):
        course_score_sum += student_contest.score
        course_score_max += contest.score_max

        if contest.is_necessary:
            necessary_contests_results.append(student_contest.is_ok)

    count_necessary_contests = len(necessary_contests_results)
    contests_ok = sum(necessary_contests_results)
    contests_ok_percent = 100 * contests_ok / count_necessary_contests
    score_percent = 100 * course_score_sum / course_score_max
    if course.ok_method == 'contests_ok':
        perc_ok = contests_ok_percent
    elif course.ok_method == 'score_sum':
        perc_ok = score_percent
    else:
        logger.error('Unknown ok_method: %s', course.ok_method)
        raise ValueError(f'Unknown ok_method: {course.ok_method}')

    is_ok = perc_ok >= course.ok_threshold_perc

    if student_course.score < course_score_sum:
        student_course.score = course_score_sum
        session.add(student_course)
    if student_course.contests_ok < contests_ok:
        student_course.contests_ok = contests_ok
        session.add(student_course)
    if student_course.contests_ok_percent < contests_ok_percent:
        student_course.contests_ok_percent = contests_ok_percent
        session.add(student_course)
    if student_course.score_percent < score_percent:
        student_course.score_percent = score_percent
        session.add(student_course)
    if not student_course.is_ok and is_ok:
        student_course.is_ok = is_ok
        session.add(student_course)
