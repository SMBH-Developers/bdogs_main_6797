from datetime import datetime, date

from sqlalchemy import select, update, delete, Row, func
from sqlalchemy.dialects.postgresql import insert

from loguru import logger

from src.models._engine import async_session
from ._models import *


FunnelUser = Row[int, datetime, str, datetime, datetime | None]


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


"""Работа с отправкой сообщений"""


async def get_users_by_status(status: str = 'alive') -> list[FunnelUser]:
    """Статус по умолчанию 'alive'"""
    async with async_session() as session:
        users = (await session.execute(select(User.id, User.funnel_timestamp, User.step, User.last_message_at_user, User.last_message_at_bot).where(User.status == status, User.step != '1-0', User.folder == 'Ве'))).all()
    return users


async def get_user_registration(id_: int):
    async with async_session() as session:
        registration_date = (await session.execute(select(User.registration_date).where(User.id == id_))).scalar_one_or_none()
    return registration_date


async def get_user_step(id_: int):
    async with async_session() as session:
        step = (await session.execute(select(User.step).where(User.id == id_))).scalar_one()
    return step


async def set_status(id_: int, status: str):
    """Обновление статуса"""
    async with async_session() as session:
        await session.execute(update(User).values(status=status).where(User.id == id_))
        await session.commit()
        logger.info(f"DATABASE | [{id_}] Update User status - {status}")


async def set_day_message(id_: int, day: int, message: int):
    """Обновление полученного дня и сообщения"""
    async with async_session() as session:
        await session.execute(update(User).values(step=f'{day}-{message}').where(User.id == id_))
        await session.commit()
        logger.info(f"DATABASE | [{id_}] Update User step - {day}-{message}")


async def update_last_message_at_bot(id_: int):
    """Обновление последнего сообщения от нас"""
    async with async_session() as session:
        await session.execute(update(User).values(last_message_at_bot=func.now()).where(User.id == id_))
        await session.commit()
        logger.info(f"DATABASE | [{id_}] Update last message at bot")


async def update_last_message_at_user(id_: int):
    """Обновление последнего сообщения от юзера"""
    async with async_session() as session:
        await session.execute(update(User).values(last_message_at_user=func.now()).where(User.id == id_))
        await session.commit()
        logger.info(f"DATABASE | [{id_}] Update last message at user")


async def get_funnel_timestamp(id_: int):
    async with async_session() as session:
        funnel_tmp = (await session.execute(select(User.funnel_timestamp).where(User.id == id_))).scalar_one_or_none()
    return funnel_tmp


async def get_user_reply(id_: int):
    async with async_session() as session:
        user_reply = (await session.execute(select(User.last_message_at_user).where(User.id == id_))).scalar_one_or_none()
    return user_reply


async def get_bot_reply(id_: int):
    async with async_session() as session:
        bot_reply = (await session.execute(select(User.last_message_at_bot).where(User.id == id_))).scalar_one_or_none()
    return bot_reply
