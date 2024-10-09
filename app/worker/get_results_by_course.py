import loguru

from app.database.connection import SessionManager
from app.schemas import StudentResults
from app.utils import course as course_utils
from app.utils import department as department_utils
from app.utils import results as results_utils
from app.utils import student as student_utils


async def task(
    course_short_name: str,
    student_login: str,
    base_logger: 'loguru.Logger',
) -> list[str]:
    logger = base_logger
    headers = {'log-contest-login': student_login}
    async with SessionManager().create_async_session() as session:
        student = await student_utils.get_student_or_raise(
            session, student_login, headers=headers
        )
        course = await course_utils.get_course_by_short_name(
            session, course_short_name
        )
        department = await department_utils.get_department_by_student(
            session, student.id
        )
        if course is None:
            text = _get_error_message_404(
                student_login=student_login,
                detail='Course not found',
            )
            return [text]
        student_course = await course_utils.get_student_course(
            session, student.id, course.id
        )
        if student_course is None:
            text = _get_error_message_404(
                student_login=student_login,
                detail='Student not registered on course',
            )
            return [text]
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

    result = _get_student_results_messages(
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
            department=department.name,
        ),
        student_login=student.contest_login,
    )
    return result


def _get_error_message_404(
    student_login: str,
    detail: str,
) -> str:
    return f"""Кажется, что-то не так с твоим логином.
Текущий записанный логин: {student_login}
Если что-то не так, пожалуйста, пройди регистрацию еще раз, чтобы система обновила твой логин.
Если логин правильный - напиши нам, пройдя по кнопкам Меню (/start) —> Общая информация —> Задать вопрос.
Подробности ошибки: {detail}"""


def _get_student_results_messages(
    results: StudentResults,
    student_login: str,
) -> list[str]:
    messages = [
        f"""
Логин: {student_login}
ФИО для проверки: {results.fio}
Факультет: {results.department}
""".strip()
    ]
    # pylint: disable=too-many-nested-blocks
    for course_results in results.courses:
        results_msg = f'Курс: {course_results.name}\n'
        if course_results.str_need:
            results_msg += f'{course_results.str_need}\n'
        if course_results.course_levels:
            results_msg += '\n'
            for course_level in course_results.course_levels:
                results_msg += (
                    f'{course_level.name}: '
                    f'{"✅" if course_level.is_ok else "НЕТ❌"}\n'
                )
            results_msg += '\n'
        for contest_results in course_results.contests:
            results_msg += f"""
- {contest_results.name}
-- {contest_results.link}
-- Дедлайн: {contest_results.deadline}
-- Набрано баллов {contest_results.score} из {contest_results.score_max}
"""
            if contest_results.is_final:
                results_msg += (
                    '-- Контест зачтен '
                    f'{"✅" if contest_results.is_ok else "НЕТ❌"}\n'
                )
            else:
                results_msg += (
                    '-- Набрано баллов без учета дедлайна '
                    f'{contest_results.score_no_deadline}\n'
                )
                for contest_level in contest_results.levels:
                    need_score_msg = f'{contest_level.score_need} '
                    if contest_level.include_after_deadline:
                        need_score_msg += '(без учета дедлайна)'
                    results_msg += (
                        f'-- Необходимо баллов на {contest_level.name}: '
                        f'{need_score_msg}'
                        f', {"набрано✅" if contest_level.is_ok else "НЕТ❌"}\n'
                    )

        messages.append(results_msg.strip())  # TODO: check length

    return messages
