import datetime as dt
import shutil
import traceback
from pathlib import Path

import loguru
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import constants
from app.bot_helper import send
from app.database.connection import SessionManager
from app.database.models import User
from app.schemas import StudentResults
from app.utils.common import fill_pdf
from app.utils.course import (
    get_all_active_courses,
    get_course_by_short_name,
    get_course_levels,
    get_or_create_student_course_level,
    get_student_courses,
)
from app.utils.results import get_student_course_results
from app.utils.student import get_student
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
    request: Request,
    student_login: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> JSONResponse:
    """
    Get student results for a specific course.
    """
    logger = loguru.logger.bind(
        uuid=request['request_id'], student={'contest_login': student_login}
    )
    headers = {'log_contest_login': student_login}
    student = await get_student(session, student_login)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Student not found',
            headers=headers,
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
                    logger,
                    session,
                )
                for course, student_course in await get_student_courses(
                    session, student.id
                )
            ],
            fio=student.fio,
        ),
        headers=headers,
    )


@api_router.post(
    '/fill/{course_short_name}',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def fill_results(
    file: UploadFile,
    course_short_name: str,
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(SessionManager().get_async_session),
) -> FileResponse:
    course = await get_course_by_short_name(session, course_short_name)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Course not found',
        )
    with open('temp.pdf', 'wb') as f:
        f.write(await file.read())
    result_path = await fill_pdf(
        'temp.pdf',
        course.id,
        session,
        result_filename=f'{course_short_name}_{file.filename}',
    )
    Path('temp.pdf').unlink()
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
    logger = loguru.logger.bind(uuid=request['request_id'])

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

    tmp_path = Path('temp')
    if tmp_path.exists():
        shutil.rmtree(tmp_path)
    tmp_path.mkdir()

    # unarchive in temp folder
    with open('temp.zip', 'wb') as f:
        f.write(await file_archive.read())
    shutil.unpack_archive('temp.zip', 'temp')
    Path('temp.zip').unlink()

    results_path = Path('temp_results')
    if results_path.exists():
        shutil.rmtree(results_path)
    results_path.mkdir()

    # fill all pdfs in temp folder
    for filename in tmp_path.iterdir():
        if filename.suffix == '.pdf':
            logger.info('Filling {}', filename)
            try:
                await fill_pdf(
                    filename,
                    course.id,
                    session,
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
