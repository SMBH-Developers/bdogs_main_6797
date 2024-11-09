from datetime import datetime
from dataclasses import dataclass

import pytest
from pyrogram import Client
from sqlalchemy import delete, insert
import redis.asyncio as aioredis

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.constants import SESSIONS_DIR
from src.models import User, async_session
from src.config import settings


@dataclass
class MockChat:
    id: int

@dataclass
class MockMessage:
    chat: MockChat
    id: int
    date: datetime


@pytest.fixture(scope='session')
async def scheduler():
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.start()
    yield scheduler
    scheduler.remove_all_jobs('default')
    scheduler.shutdown(wait=False)


@pytest.fixture(scope='session')
async def get_client():
    client = Client(
        str(SESSIONS_DIR / 'test_session'),
        settings.api_id,
        settings.api_hash,
        phone_number=settings.phone_number
    )

    await client.start()
    yield client
    await client.stop()


@pytest.fixture(scope='class')
async def user_id():
    '''Реальный ID пользователя'''
    return 7069852252

@pytest.fixture
async def chat_id():
    '''Реальный ID чата'''
    return 1371617744


@pytest.fixture
async def job_time():
    '''Время выполнения задачи в минутах'''
    return 1

@pytest.fixture(scope='class')
async def job_id(user_id):
    '''ID задачи'''
    return f'ping_{user_id}'

    
@pytest.fixture
async def message(chat_id):
    return MockMessage(chat=MockChat(id=chat_id), id=1, date=datetime.now())


@pytest.fixture(scope='session')
async def redis_client():
    redis_client = aioredis.from_url(
        url=f'{settings.redis_uri}/0',
        decode_responses=True,
        protocol=3,
        retry_on_timeout=True
    )
    yield redis_client
    await redis_client.aclose()


@pytest.fixture
async def db_session():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e


@pytest.fixture(scope='class')
async def add_user(user_id: int):
    async with async_session() as session:
        try:
            await session.execute(insert(User).values(id=user_id))
            await session.commit()
        except Exception as e:
            await session.rollback()
        
        yield
        
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
