from datetime import datetime, date

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from loguru import logger

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


async def set_folder(id_: int, folder: str):
    async with async_session() as session:
        await session.execute(update(User).values(folder=folder).where(User.id == id_))
        await session.commit()
    logger.success(f'[id_] Update folder - {folder}')


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


async def insert_cards(cards: dict[int, str]):
    async with async_session() as session:
        await session.execute(delete(Card))
        for card, status in cards.items():
            await session.execute(insert(Card).values(card=card, status=status).on_conflict_do_nothing())
        await session.commit()


async def update_cards_status(card: int, status: str):
    async with async_session() as session:
        exists = (await session.execute(select(Card.card).where(Card.card == card).limit(1))).one_or_none()
        if exists:
            await session.execute(update(Card).values(status=status).where(Card.card == card))
        else:
            await session.execute(insert(Card).values(card=card, status=status))
        await session.commit()


async def check_card_status(card: int) -> bool:
    async with async_session() as session:
        status = (await session.execute(select(Card.status).where(Card.card == card).limit(1))).one_or_none()
        bool_status: bool
        if status is not None and status[0] == 'black':
            bool_status = False
        else:
            bool_status = True
    return bool_status


async def get_old_users(limit: int, users: set):
    async with async_session() as session:
        old_users = (await session.execute(select(User.id).where(User.id.in_(users)).limit(limit))).scalars().all()
    return old_users


async def update_managers_list(new_manager: str):
    async with async_session() as session:
        managers = (await session.execute(select(ManagerList.managers))).scalar_one()
        new_managers = managers+' '+new_manager
        await session.execute(update(ManagerList).values(mangers=new_managers))
        await session.commit()


async def get_managers_list() -> list[str]:
    async with async_session() as session:
        managers = (await session.execute(select(ManagerList.managers))).scalar_one()
    return managers.split(' ')
