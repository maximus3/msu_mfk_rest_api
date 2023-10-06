import datetime as dt
import shutil
import traceback
from pathlib import Path

import loguru
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import constants, worker
from app.bot_helper import send
from app.database.connection import SessionManager
from app.database.models import User
from app.limiter import limiter
from app.schemas import StudentResults
from app.utils import course as course_utils
from app.utils import pdf
from app.utils import student as student_utils
from app.utils.course import (
    get_all_active_courses,
    get_course_by_short_name,
    get_course_levels,
    get_or_create_student_course_level,
    get_student_courses,
)
from app.utils.results import get_student_course_results
from app.utils.user import get_current_user


api_router = APIRouter(
    prefix='/results',
    tags=['Results'],
)


@api_router.get(
    '/all/{student_login}',
    response_model=StudentResults,
    status_code=status.HTTP_200_OK,
)
async def get_all_results(
    _: Request,
    student_login: str,
    __: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> JSONResponse:
    """
    Get student results for all courses.
    """
    headers = {'log-contest-login': student_login}
    student = await student_utils.get_student_or_raise(
        session, student_login, headers=headers
    )
    all_courses = await get_all_active_courses(session)
    levels_by_course = {
        course.id: await get_course_levels(session, course.id)
        for course in all_courses
    }
    return JSONResponse(
        StudentResults(
            courses=[
                await get_student_course_results(
                    student,
                    course,
                    levels_by_course[course.id],
                    student_course,
                    [
                        await get_or_create_student_course_level(
                            session, student.id, course.id, course_level.id
                        )
                        for course_level in levels_by_course[course.id]
                    ],
                    student_course_contest_data=(
                        await course_utils.get_student_course_contests_data(
                            session, course.id, student.id
                        )
                    ),
                    logger=loguru.logger,
                )
                for course, student_course in await get_student_courses(
                    session, student.id
                )
            ],
            fio=student.fio,
        ).dict(),
        headers=headers,
    )


@api_router.get(
    '/by-course/{course_short_name}',
    status_code=status.HTTP_200_OK,
)
@limiter.limit('5/10seconds')
async def get_results_by_course(
    request: Request,  # pylint: disable=unused-argument
    course_short_name: str,
    _: User = Depends(get_current_user),
) -> JSONResponse:
    """
    Get student results for a specific course.
    """
    logger = loguru.logger.bind(
        course={'short_name': course_short_name},
    )
    task = worker.get_results_by_course_task.delay(
        course_short_name=course_short_name,
        student_login=request.headers['log-contest-login'],
        student_tg_id=request.headers['log-tg-id'],
        request_id=request.scope['request_id'],
    )
    logger = logger.bind(
        task_id=task.id,
    )
    logger.info('Task {} sent to celery', task.id)
    return JSONResponse({'task_id': task.id})


@api_router.get(
    '/task/status',
    status_code=status.HTTP_200_OK,
)
async def get_task_status(
    request: Request,  # pylint: disable=unused-argument
    task_id: str,
    _: User = Depends(get_current_user),
) -> JSONResponse:
    status_to_name = {
        'PENDING': 'Ожидание выполнения задачи',
        'STARTED': 'В работе',
        'RETRY': 'В работе (повтор)',
        'FAILURE': 'Ошибка при получении результатов, '
        'попробуйте еще раз или напишите администратору.',
        'SUCCESS': 'Результаты отправлены. Если сообщение с '
        'резльтатами до сих пор вам не пришло, '
        'пожалуйста, обратитесь к администратору.',
    }
    logger = loguru.logger.bind(
        task_id=task_id,
    )
    result = AsyncResult(task_id)
    logger.info('Current task status: {}', result.status)
    return JSONResponse(
        {
            'status': result.status,
            'description': status_to_name.get(result.status),
        }
    )


@api_router.post(
    '/fill/{course_short_name}',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def fill_results(
    request: Request,
    file: UploadFile,
    course_short_name: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> FileResponse:
    logger = loguru.logger.bind(
        course={'short_name': course_short_name},
    )
    course = await get_course_by_short_name(session, course_short_name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    tmp_filename = f'{request["request_id"]}.pdf'
    with open(tmp_filename, 'wb') as f:
        f.write(await file.read())
    result_path = await pdf.fill_pdf(
        filename=tmp_filename,
        course_id=course.id,
        logger=logger,
        session=session,
        result_filename=f'{course_short_name}_{file.filename}',
    )
    Path(tmp_filename).unlink()
    return FileResponse(
        result_path,
        media_type='application/octet-stream',
        filename=result_path.name,
    )


@api_router.post(
    '/fill/{course_short_name}/archive',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def fill_results_archive(  # pylint: disable=too-many-statements
    request: Request,
    file_archive: UploadFile,
    course_short_name: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> FileResponse:
    logger = loguru.logger.bind(
        course={'short_name': course_short_name},
    )

    if not file_archive.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File must be zip archive',
        )
    course = await get_course_by_short_name(session, course_short_name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )

    tmp_dir_name = request['request_id']
    tmp_path = Path(tmp_dir_name)
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir()

    # unarchive in temp folder
    tmp_zip_filename = f'{request["request_id"]}.zip'
    with open(tmp_zip_filename, 'wb') as f:
        f.write(await file_archive.read())
    shutil.unpack_archive(tmp_zip_filename, tmp_dir_name)
    Path(tmp_zip_filename).unlink()

    tmp_results_dir_name = request['request_id'] + '_results'
    results_path = Path(tmp_results_dir_name)
    if results_path.exists():
        shutil.rmtree(results_path)
    results_path.mkdir()

    # fill all pdfs in temp folder
    for filename in tmp_path.iterdir():
        if filename.suffix == '.pdf':
            logger.info('Filling {}', filename)
            try:
                await pdf.fill_pdf(
                    filename=filename,
                    course_id=course.id,
                    logger=logger,
                    session=session,
                    result_filename=f'{course_short_name}_{filename.name}',
                    result_path=results_path,
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception('Error while filling pdf', exc_info=exc)
                try:
                    await send.send_traceback_message(
                        f'Error while filling pdf {filename.name}: {exc}',
                        code=traceback.format_exc(),
                    )
                except Exception as send_exc:  # pylint: disable=broad-except
                    logger.exception(
                        'Error while sending message', exc_info=send_exc
                    )

    shutil.make_archive(
        f'{course_short_name}_'
        f'{dt.datetime.now().strftime(constants.dt_format_filename)}',
        'zip',
        results_path,
    )
    shutil.rmtree(tmp_path)
    shutil.rmtree(results_path)
    return FileResponse(
        f'{course_short_name}_'
        f'{dt.datetime.now().strftime(constants.dt_format_filename)}.zip',
        media_type='application/octet-stream',
        filename=f'{course_short_name}_'
        f'{dt.datetime.now().strftime(constants.dt_format_filename)}.zip',
    )
