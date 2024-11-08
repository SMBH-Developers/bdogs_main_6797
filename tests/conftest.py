from datetime import datetime
from dataclasses import dataclass

import pytest

from src.tasks.scheduler_singl import SchedulerSingleton
from src.config import client


@dataclass
class MockChat:
    id: int

@dataclass
class MockMessage:
    chat: MockChat
    id: int
    date: datetime


@pytest.fixture
async def scheduler():
    scheduler = SchedulerSingleton({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.start()
    yield scheduler
    scheduler.shutdown()


@pytest.fixture
async def client():
    client.start()
    yield client
    client.stop()


@pytest.fixture
async def user_id():
    return 1234567890


@pytest.fixture
async def job_time():
    '''Время выполнения задачи в минутах'''
    return 1

    
@pytest.fixture
async def message():
    return MockMessage(chat=MockChat(id=1), id=1, date=datetime.now())
