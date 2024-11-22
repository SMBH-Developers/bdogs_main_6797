from datetime import datetime, date
from typing import Literal, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.dialects.postgresql import insert

from loguru import logger

from src.database._engine import async_session
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


async def set_send_message(id_: int):
    async with async_session() as session:
        await session.execute(update(User).values(get_message=True).where(User.id == id_))
        await session.commit()
    logger.success(f'[{id_}] Update get message on True')


async def get_message(id_: int) -> bool:
    async with async_session() as session:
        message = (await session.execute(select(User.get_message).where(User.id == id_))).one_or_none()
    print(message)
    return message[0]


async def set_folder(id_: int, folder: str):
    async with async_session() as session:
        await session.execute(update(User).values(folder=folder).where(User.id == id_))
        await session.commit()
    logger.success(f'[{id_}] Update folder - {folder}')


async def check_folder(id_: int) -> str | None:
    async with async_session() as session:
        folder = (await session.execute(select(User.folder).where(User.id == id_))).scalar_one_or_none()
    return folder


async def get_count_without_folder() -> int:
    async with async_session() as session:
        count = (await session.execute(select(func.count('*')).select_from(User).where(User.folder.is_(None), User.registration_date >= datetime.now().replace(hour=0, minute=0)))).scalar_one()
    return count


async def get_managers_today() -> str | None:
    today = datetime.now().date()
    async with async_session() as session:
        stmt = select(Shift.managers).where(Shift.date == today)
        managers = (await session.execute(stmt)).scalar_one_or_none()
    return managers


async def set_managers_shifts(shifts: dict[date, str]):
    '''shifts: {'2024-11-09': 'Ве Та Ан Су'}'''
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
        await session.execute(update(ManagerList).values(managers=new_managers))
        await session.commit()


async def get_managers_list() -> list[str]:
    async with async_session() as session:
        managers = (await session.execute(select(ManagerList.managers))).scalar_one()
    print(managers.split(' '))
    return managers.split(' ')

async def set_ping_step(id_: int, step: Optional[Literal['FIRST', 'SECOND', 'THIRD']]):
    async with async_session() as session:
        try:
            await session.execute(update(User).values(ping_step=step).where(User.id == id_))
            await session.commit()
        except Exception as e:
            logger.error(f'[{id_}] Error update ping step: {e}')
            await session.rollback()
        
async def get_ping_step(id_: int) -> Optional[Literal['FIRST', 'SECOND', 'THIRD']]:
    async with async_session() as session:
        step = (await session.execute(select(User.ping_step).where(User.id == id_))).scalar_one_or_none()
        await session.commit()
    return step