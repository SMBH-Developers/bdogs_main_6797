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
from src.tasks import close_job


async def ping(
    client: Client,
    user_id: int,
    message: types.Message,
    scheduler = SchedulerSingleton(),
    job_time: int = 20
) -> Optional[str]:
    '''После автоматезированного сообщения создает задачу в schedule на 20 минут
    '''
    try:
        await db.set_ping_step(user_id, 'FIRST')
        job_id = f'ping_{user_id}'
        scheduler.add_job(
            trigger='interval',
            run_date=datetime.now(),
            minutes=job_time,
            func=chain_ping,
            kwargs={
                'user_id': user_id,
                'client': client,
                'message': message,
                'scheduler': scheduler,
                'job_id': job_id
            },
            id=job_id,
            replace_existing=True,
            misfire_grace_time=60,
            coalesce=True
        )
        logger.info(f'Ping task for user {user_id} created')
        return job_id
    
    except BaseException as e:
        logger.error(f'Error creating ping task for user {user_id}: {e}')


@close_job
async def chain_ping(
    user_id: int,
    client: Client,
    message: types.Message,
    scheduler: SchedulerSingleton,
    job_id: str
) -> Optional[types.Message]:
    '''
    Проверяет последнее сообщение пользователя и проверяет его статус
    Если условия выполнены, то отправляет пинг
    Иначе удаляет задачу.
    '''
    
    if (
        (ping_step := await db.get_ping_step(user_id))
        and await is_last_message_time(client, user_id, message)
        and await is_last_message_time_read(client, message)
    ):
        if message := await send_ping(
            client,
            user_id,
            ping_step,
            name=name if (name := await get_name(user_id)) else ''
        ):
            await db.set_ping_step(user_id, PingText.get_next_step(ping_step))
            return message
        else:
            await db.set_ping_step(user_id, None)
            
    return 