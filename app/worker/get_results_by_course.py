import asyncio
import functools

import loguru

from app.bot_helper import bot
from app.database import models
from app.database.connection import SessionManager
from app.schemas import StudentResults
from app.utils import course as course_utils
from app.utils import results as results_utils
from app.utils import student as student_utils


def async_to_sync(func):  # type: ignore
    @functools.wraps(func)
    def wrapped(*args, **kwargs):  # type: ignore
        return asyncio.run(func(*args, **kwargs))

    return wrapped


@async_to_sync
async def task(
    course_short_name: str,
    student_login: str,
    student_tg_id: str,
) -> bool:
    logger = loguru.logger.bind(
        course={'short_name': course_short_name},
    )
    headers = {'log-contest-login': student_login}
    async with SessionManager().create_async_session() as session:
        student = await student_utils.get_student_or_raise(
            session, student_login, headers=headers
        )
        course = await course_utils.get_course_by_short_name(
            session, course_short_name
        )
        if course is None:
            await _send_error_message_404(
                student_login=student_login,
                student_tg_id=student_tg_id,
                detail='Course not found',
            )
            return False
        student_course = await course_utils.get_student_course(
            session, student.id, course.id
        )
        if student_course is None:
            await _send_error_message_404(
                student_login=student_login,
                student_tg_id=student_tg_id,
                detail='Student not registered on course',
            )
            return False
        levels_by_course = await course_utils.get_course_levels(
            session, course.id
        )
        student_course_levels = [
            await course_utils.get_or_create_student_course_level(
                session, student.id, course.id, course_level.id
            )
            for course_level in levels_by_course
        ]
        student_course_contest_data = (
            await course_utils.get_student_course_contests_data(
                session, course.id, student.id
            )
        )

    await _send_student_results(
        results=StudentResults(
            courses=[
                await results_utils.get_student_course_results(
                    student,
                    course,
                    levels_by_course,
                    student_course,
                    student_course_levels,
                    student_course_contest_data,
                    logger=logger,
                )
            ],
            fio=student.fio,
        ),
        student=student,
    )

    return True


async def _send_error_message_404(
    student_login: str,
    student_tg_id: str,
    detail: str,
) -> None:
    await bot.bot_students.send_message(
        chat_id=student_tg_id,
        text=f'''Кажется, что-то не так с твоим логином.
Текущий записанный логин: {student_login}
Если что-то не так, пожалуйста, пройди регистрацию еще раз, чтобы система обновила твой логин.
Если логин правильный - напиши нам вопрос через раздел "Другое".
Подробности ошибки: {detail}''',
    )


async def _send_student_results(
    results: StudentResults,
    student: models.Student,
) -> None:
    await bot.bot_students.send_message(
        chat_id=student.tg_id,
        text=f'''
Логин: {student.contest_login}
ФИО для проверки: {results.fio}
''',
    )

    for course_results in results.courses:
        results_msg = (
            f'Курс: {course_results.name}\n{course_results.str_need}\n\n'
        )
        for course_level in course_results.course_levels:
            results_msg += (
                f'{course_level.name}: '
                f'{"✅" if course_level.is_ok else "НЕТ❌"}\n'
            )
        results_msg += '\n'
        for contest_results in course_results.contests:
            results_msg += f'''
- {contest_results.name}
-- {contest_results.link}
-- Дедлайн: {contest_results.deadline}
-- Набрано баллов {contest_results.score} из {contest_results.score_max}
'''
            if contest_results.is_final:
                results_msg += (
                    '-- Контест зачтен '
                    f'{"✅" if contest_results.is_ok else "НЕТ❌"}\n'
                )
            else:
                results_msg += (
                    '-- Набрано баллов без учета дедлайна '
                    f'{contest_results.score_no_deadline}'
                )
                for contest_level in contest_results.levels:
                    need_score_msg = f'{contest_level.score_need} '
                    if contest_level.include_after_deadline:
                        need_score_msg += 'без учета дедлайна)'
                    results_msg += (
                        f'-- Необходимо баллов на {contest_level.name}: '
                        f'{need_score_msg}'
                        f', {"набрано✅" if contest_level.is_ok else "НЕТ❌"}\n'
                    )

        await bot.bot_students.send_message(
            chat_id=student.tg_id,
            text=results_msg,  # TODO: check length
        )
