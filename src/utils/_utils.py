import asyncio
from typing import List, Sequence
from datetime import datetime, timedelta, time

from pyrogram import types, errors
from loguru import logger
from sqlalchemy import Row

from src.funnel import FunnelConfig
from src.models.db import FunnelUser
from src.funnel.types import MyGeneratedMessage


__all__ = ["get_date_by_weekday", "extract_card_from_command", "gather_tasks_buffer", "filter_users"]


def get_date_by_weekday(day: str):
    days = {'понедельник': 0, 'вторник': 1, 'среда': 2,
            'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}

    today = datetime.now()
    target_weekday = days[day.lower()]
    if today.weekday() == 6 and today.time() >= time(hour=16):
        days_ahead = target_weekday + 1
    else:
        days_ahead = (target_weekday - today.weekday())

    day_date = today + timedelta(days=days_ahead)
    return day_date


async def extract_card_from_command(message: types.Message) -> str | None:
    if len(message.command) < 2:
        await message.reply('Ошибка: Пожалуйста, укажите номер карты💳.')
        return

    card = message.command[1] if len(message.command) == 2 else ' '.join(message.command[1:])

    if not card.replace(' ', '').isdigit() or 16 < len(card) > 19:
        await message.reply("Ошибка: карта должна содержать только 16 цифр.")
        return

    return card


# Работа с сообщениями
async def gather_tasks_buffer(tasks: List[asyncio.Task], *, ignore_length: bool = False):
    if len(tasks) >= 20 or ignore_length:
        await _gather_tasks(tasks)
        tasks.clear()


async def _gather_tasks(tasks: List):
    results = await asyncio.gather(*tasks, return_exceptions=True)
    exceptions = [ex for ex in results if isinstance(ex, Exception)]
    if len(exceptions) > 0:
        print(f'{len(exceptions)=}')
    try:
        with logger.catch(level="DEBUG"):
            for exception in exceptions:
                if not isinstance(exception, (errors.PeerIdInvalid, errors.InputUserDeactivated)):
                    raise exception
    except:
        pass


async def _get_user_funnel_message(id_: int, day: str, step: str | int) -> MyGeneratedMessage | None:
    if day in FunnelConfig.config.diff_days_to_func:
        messages = (await FunnelConfig().get_message(id_, day))[int(step):]
        if messages:
            return messages[0]


async def should_get_message(user: Row[int, datetime, str, datetime, datetime | None, str]):
    day, step = user.step.split('-')
    message = await _get_user_funnel_message(user.id, day, int(step))
    if message is None:
        # logger.error(f'SYSTEM | [{user.id}] Empty list of messages. step: {day}-{step}')
        return True  # TODO normal
    return await message.filter(user.id, day, step,
                                funnel_timestamp=user.funnel_timestamp,
                                bot_reply=user.last_message_at_bot, user_reply=user.last_message_at_user)


async def filter_users(users: Sequence[FunnelUser]) -> Sequence[FunnelUser]:
    """
    Filter users by funnel skip days and time
    :param users: [id, registration_date, step (e.g. 0-0), funnel]
    """
    users = [user for user in users if (
        (datetime.now() - user.funnel_timestamp).total_seconds() > (int(user.step.split('-')[0]) * 24 * 60 * 60)
    )]

    users = [user for user in users if await should_get_message(user)]

    return users
