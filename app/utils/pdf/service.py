import dataclasses
import io
from pathlib import Path
from uuid import UUID

import loguru
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.connection import SessionManager
from app.utils.student import get_student_course_is_ok


pdfmetrics.registerFont(
    TTFont(
        'FreeSans',
        get_settings().BASE_DIR / 'static' / 'ttf' / 'FreeSans.ttf',
    )
)


@dataclasses.dataclass
class Point:
    x: float
    y: float


def visitor_body(  # pylint: disable=too-many-arguments,too-many-nested-blocks
    text: str,
    _: list[float],  # cm
    tm: list[float],
    __: float,  # font_dict
    font_size: float,
    params_text: dict[str, tuple[str, Point | None]],
    list_of_students: dict[str, list[list[float | str]]],
    visitor_dict: dict[str, int | bool],
) -> None:
    x = tm[4]
    y = tm[5]
    text = text.strip()
    for key in params_text:
        if params_text[key][1] is None and text == params_text[key][0]:
            params_text[key] = (params_text[key][0], Point(x, y))
            visitor_dict['count'] += 1
            return
    if visitor_dict['count'] == len(params_text):
        if text in ('Расшифровка подписей:', ''):
            return
        for key in params_text:
            if x == params_text[key][1].x:  # type: ignore
                if key == 'num':
                    visitor_dict['was_num'] = True
                    list_of_students[key].append([y, font_size, text])
                else:
                    if visitor_dict['was_num']:
                        list_of_students[key].append([y, font_size, text])
                        visitor_dict['was_num'] = False
                    elif key == 'fio':
                        # pylint: disable=line-too-long
                        list_of_students[key][-1][2] += f' {text}'  # type: ignore
                        # pylint: enable=line-too-long
                    else:
                        list_of_students[key].append([y, font_size, text])


async def fill_pdf(  # pylint: disable=too-many-statements,too-many-arguments
    filename: str | Path,
    course_id: UUID,
    logger: 'loguru.Logger',
    session: AsyncSession | None = None,
    result_filename: str = 'result.pdf',
    result_path: str | Path = './tmp',
) -> Path:
    if session is None:
        async with SessionManager().create_async_session() as session:
            return await fill_pdf(
                filename=filename,
                course_id=course_id,
                logger=logger,
                session=session,
                result_filename=result_filename,
                result_path=result_path,
            )

    reader = PdfReader(filename)
    writer = PdfFileWriter()

    num_pages = reader.getNumPages()
    logger.info('Filename have {} pages', num_pages)

    for page_num in range(num_pages):

        list_of_students: dict[str, list[list[float | str]]] = {
            'num': [],
            'fio': [],
            'mark': [],
            'sign': [],
        }
        params_text: dict[str, tuple[str, Point | None]] = {
            'num': ('№', None),
            'fio': ('Фамилия Имя Отчество', None),
            'mark': ('Оценка', None),
            'sign': ('Подпись', None),
        }
        page = reader.pages[page_num]

        visitor_dict = {'count': 0, 'was_num': False}

        # pylint: disable=cell-var-from-loop
        page.extract_text(
            visitor_text=lambda *args: visitor_body(  # type: ignore
                *args,
                params_text=params_text,
                list_of_students=list_of_students,
                visitor_dict=visitor_dict,
            )
        )
        # pylint: enable=cell-var-from-loop

        if len(list_of_students['num']) == 0:
            continue

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        for i in range(len(list_of_students['num'])):
            can.setFont('FreeSans', list_of_students['num'][i][1])
            y = list_of_students['num'][i][0]
            x = params_text['mark'][1].x  # type: ignore
            if await get_student_course_is_ok(
                session,
                course_id,
                list_of_students['fio'][i][2],  # type: ignore
                logger=logger,
            ):
                can.drawString(x, y, 'Зачет')
            # else:
            #     can.drawString(x, y, 'Незачет')
        can.save()

        # move to the beginning of the StringIO buffer
        packet.seek(0)

        new_pdf_page = PdfFileReader(packet)

        if new_pdf_page.getNumPages() != 0:
            page.mergePage(new_pdf_page.getPage(0))
        writer.addPage(page)

    # formatted_dt = dt.datetime.now().strftime(
    #     constants.dt_format_filename
    # )
    # result_filename = (
    #     f'result_{formatted_dt}.pdf'
    # )

    path = Path(result_path)
    path.mkdir(parents=True, exist_ok=True)

    with open(path / result_filename, 'wb') as output_stream:
        writer.write(output_stream)

    return path / result_filename
