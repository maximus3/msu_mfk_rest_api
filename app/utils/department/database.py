from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Department


async def get_department(
    session: AsyncSession, name: str
) -> Department | None:
    query = select(Department).where(Department.name == name)
    return await session.scalar(query)


async def get_all_departments(session: AsyncSession) -> list[Department]:
    query = select(Department)
    return (await session.execute(query)).scalars().all()
