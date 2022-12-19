# pylint: disable=too-many-arguments

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import SessionManager
from app.database.models import TQDMLogs


async def get_sql_tqdm(
    session: AsyncSession,
    name: str,
) -> TQDMLogs | None:
    query = select(TQDMLogs).where(TQDMLogs.name == name)
    return await session.scalar(query)


async def write_sql_tqdm(
    name: str,
    current: int,
    total: int | None,
    need_time: str,
    need_time_for_all: str,
    avg_data: str,
    all_time: str,
) -> None:
    async with SessionManager().create_async_session() as session:
        model = await get_sql_tqdm(session, name)
        if model is None:
            model = TQDMLogs(
                name=name,
                current=current,
                total=total,
                need_time=need_time,
                need_time_for_all=need_time_for_all,
                avg_data=avg_data,
                all_time=all_time,
            )
            session.add(model)
        else:
            model.current = current
            model.total = total
            model.need_time = need_time
            model.need_time_for_all = need_time_for_all
            model.avg_data = avg_data
            model.all_time = all_time
            session.add(model)
