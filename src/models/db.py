from datetime import datetime, date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.models._engine import async_session
from ._models import *


async def registrate_user(id_: int):
    async with async_session() as session:
        user = User(id=id_)
        session.add(user)
        await session.commit()


async def check_user_exists(id_: int) -> bool:
    async with async_session() as session:
        exists = (await session.execute(select(User.id).where(User.id == id_).limit(1))).one_or_none()
    if exists is None:
        return False
    return True


async def get_managers_today() -> str | None:
    today = datetime.now().date()
    async with async_session() as session:
        stmt = select(Shift.managers).where(Shift.date == today)
        managers = (await session.execute(stmt)).scalar_one_or_none()
    return managers


async def set_managers_shifts(shifts: dict[date, str]):
    async with async_session() as session:
        for dt, managers in shifts.items():
            await session.execute(insert(Shift).values(date=dt, managers=managers).on_conflict_do_update(index_elements=['date'],
                                                                                                         set_={'date': dt, 'managers': managers}))
        await session.commit()
