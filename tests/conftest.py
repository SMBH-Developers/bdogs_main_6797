import asyncio
from datetime import datetime
from dataclasses import dataclass
import os

import pytest
import pytest_asyncio
from pytest_asyncio import is_async_test
from loguru import logger
from sqlalchemy import delete, insert
import redis.asyncio as aioredis
from src.tasks.scheduler_singl import SchedulerSingleton

from src.models import User, async_session
from src.config import settings
from tests.integrations.mock import MockClient, MockChat, MockMessage


# def pytest_collection_modifyitems(items):
#     pytest_asyncio_tests = (item for item in items if is_async_test(item))
#     session_scope_markers = pytest.mark.asyncio(loop_scope='session')
#     for async_test in pytest_asyncio_tests:
#         async_test.add_marker(session_scope_markers)


@pytest_asyncio.fixture(scope='session', autouse=True)
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session', autouse=True)
async def set_mode(event_loop):
    settings.MODE = 'TEST'

@pytest.fixture(scope='session')
async def get_client(message):
    return MockClient(message=message)


@pytest.fixture(scope='session')
async def scheduler(set_mode):
    scheduler = SchedulerSingleton()
    scheduler.start()
    yield scheduler
    scheduler.remove_all_jobs('default')
    scheduler.shutdown(wait=False)


@pytest.fixture(scope='session')
async def user_id():
    return 777777777


@pytest.fixture(scope='session')
async def chat_id():
    return 666666666


@pytest.fixture(scope='session')
async def job_time():
    '''Время выполнения задачи в минутах'''
    return 5

@pytest.fixture(scope='session')
async def job_id(user_id):
    '''ID задачи'''
    return f'ping_{user_id}'


@pytest.fixture(scope='session')
async def ping_step():
    '''Шаг пинга'''
    return 'FIRST'

    
@pytest.fixture(scope='session')
async def message(chat_id):
    """Создаем мок сообщения вместо реального"""
    return MockMessage(
        chat=MockChat(id=chat_id),
        id=1,
        date=datetime.now(),
        outgoing=True  # Добавляем это поле, оно нужно для проверки
    )


@pytest.fixture(scope='session')
async def redis_client(event_loop):
    redis_client = None
    try:
        redis_client = aioredis.from_url(
            url=f'{settings.redis_uri}/{settings.REDIS_JOB_DATABASES_TEST}',
            #decode_responses=True, # if hget returns raise error
            protocol=3,
            retry_on_timeout=True
        )
        if await redis_client.ping():
            yield redis_client
        else:
            logger.error('Failed to connect to Redis')
            raise Exception('Failed to connect to Redis')
    
    finally:
        if redis_client:
            try:
                await redis_client.aclose()
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")


@pytest.fixture(scope='session')
async def add_user(user_id: int):
    session = None
    try:
        session = async_session()
        await session.execute(insert(User).values(id=user_id))
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
    finally:
        if session:
            await session.close()
        
    yield

    try:
        session = async_session()
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
    finally:
        if session:
            await session.close()
