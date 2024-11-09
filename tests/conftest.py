import asyncio
from datetime import datetime
from dataclasses import dataclass

import pytest
import pytest_asyncio
from pytest_asyncio import is_async_test
from pyrogram import Client
from sqlalchemy import delete, insert
import redis.asyncio as aioredis
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.constants import SESSIONS_DIR
from src.models import User, async_session
from src.config import settings
from tests.integrations.mock import MockClient, MockChat, MockMessage


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_markers = pytest.mark.asyncio(loop_scope='session')
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_markers)


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def get_client():
    return MockClient(date=datetime.now())


@pytest.fixture(scope='session')
async def scheduler():
    jobstores = {
        'default': RedisJobStore(
            jobs_key='dispatched_trips_jobs',
            run_times_key='dispatched_trips_running',
            host=settings.REDIS_HOST_NAME,
            db=settings.REDIS_JOB_DATABASES,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD
            )
        }
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'}, jobstores=jobstores)
    scheduler.start()
    yield scheduler
    scheduler.remove_all_jobs('default')
    scheduler.shutdown(wait=False)


@pytest.fixture(scope='class')
async def user_id():
    '''Реальный ID пользователя'''
    return 1371617744

@pytest.fixture(scope='class')
async def chat_id():
    '''Реальный ID чата'''
    return 7069852252


@pytest.fixture(scope='class')
async def job_time():
    '''Время выполнения задачи в минутах'''
    return 1

@pytest.fixture(scope='class')
async def job_id(user_id):
    '''ID задачи'''
    return f'ping_{user_id}'

    
@pytest.fixture(scope='class')
async def message(chat_id):
    """Создаем мок сообщения вместо реального"""
    return MockMessage(
        chat=MockChat(id=chat_id),
        id=1,
        date=datetime.now(),
        outgoing=True  # Добавляем это поле, оно нужно для проверки
    )


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
