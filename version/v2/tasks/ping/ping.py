from typing import Optional, TypeVar
from datetime import datetime, timedelta
from loguru import logger
from pyrogram import Client
from pyrogram import types, raw

from .text import PingText
from src.database import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .utill import is_last_message_time, is_last_message_time_read, send_ping
from src.utils import get_name
from version.v2.tasks.close_job import close_job
from src.config import client

MockClient = TypeVar('MockClient')

async def ping(
    user_id: int,
    message: types.Message,
    scheduler: AsyncIOScheduler,
    job_time: int = 20,
    mock_client: Optional[MockClient] = ''
) -> Optional[str]:
    '''После автоматезированного сообщения создает задачу в schedule на 20 минут
    '''
    try:
        await db.set_ping_step(user_id, 'FIRST')
        job_id = f'ping_{user_id}'
        scheduler.add_job(
            trigger='interval',
            minutes=job_time,
            func=chain_ping,
            kwargs={
                'user_id': user_id,
                'mock_client': mock_client,
                'message': message,
                'job_id': job_id,
                'created_at': datetime.now().timestamp()
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
    message: types.Message,
    job_id: str,
    created_at: int,
    mock_client: Optional[MockClient] = None
) -> Optional[types.Message]:
    '''
    Проверяет последнее сообщение пользователя и проверяет его статус
    Если условия выполнены, то отправляет пинг
    Иначе удаляет задачу.
    '''
    client_ = mock_client or client
    if (
        (ping_step := await db.get_ping_step(user_id))
        and await is_last_message_time(client_, user_id, message)
    ):
        is_not_skip = await is_last_message_time_read(client_, message)
        if is_not_skip:
            if message := await send_ping(
                client_,
                user_id,
                ping_step,
                name=''
            ):
                await db.set_ping_step(user_id, PingText.get_next_step(ping_step))
                return message
            else:
                await db.set_ping_step(user_id, None)
        else:
            logger.info(f'Ping task {job_id} for user {user_id} SKIP')
            return 'SKIP'
            
    return
