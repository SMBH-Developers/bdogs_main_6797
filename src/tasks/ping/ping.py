from typing import Optional
from datetime import datetime, timedelta
from loguru import logger
from pyrogram import Client
from pyrogram import types, raw

from .text import PingText
from src.models import db
from src.tasks.scheduler_singl import SchedulerSingleton
from .utill import is_last_message_time, is_last_message_time_read, send_ping
from src.utils import get_name


async def ping(
    client: Client,
    user_id: int,
    message: types.Message,
    scheduler = SchedulerSingleton()
):
    '''После автоматезированного сообщения создает задачу в schedule на 20 минут
    '''
    await db.set_ping_step(user_id, 'FIRST')
    job_id = f'ping_{user_id}'
    scheduler.add_job(
        trigger='interval',
        run_date=datetime.now(),
        minutes=20,
        func=chain_ping,
        args=(
            user_id,
            client,
            message,
            scheduler,
            job_id
        ),
        id=job_id
    )
    logger.info(f'Ping task for user {user_id} created')


async def chain_ping(
    user_id: int,
    client: Client,
    message: types.Message,
    scheduler: SchedulerSingleton,
    job_id: str
):
    '''
    Проверяет последнее сообщение пользователя и проверяет его статус
    Если условия выполнены, то отправляет пинг
    Иначе удаляет задачу.
    '''
    if (
        await is_last_message_time(client, user_id, message)
        and await is_last_message_time_read(client, message)
        and (ping_step := await db.get_ping_step(user_id))
    ):
        await send_ping(
            client,
            user_id,
            ping_step,
            name=name if (name := await get_name(user_id)) else ''
        )
        await db.set_ping_step(user_id, PingText.get_next_step(ping_step))
    else:
        scheduler.remove_job(job_id) #TODO: возможно ли из исполняемой задачи удалить саму себя?
    