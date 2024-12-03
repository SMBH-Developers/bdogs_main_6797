from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.repository.base import BaseRepositoryInterface
from src.repository.cards import CardRepositoryInterface
from src.repository.shifts import ShiftRepositoryInterface

from loguru import logger

UserRepository = TypeVar("UserRepository", bound=BaseRepositoryInterface)
ShiftRepository = TypeVar("ShiftRepository", bound=ShiftRepositoryInterface)
CardRepository = TypeVar("CardRepository", bound=CardRepositoryInterface)
ManagersRepository = TypeVar("ManagersRepository", bound=BaseRepositoryInterface)


class BaseUowInterface(
    Generic[UserRepository, ShiftRepository, CardRepository, ManagersRepository], ABC
):
    user: UserRepository
    shift: ShiftRepository
    card: CardRepository
    managers: ManagersRepository
    session: Optional[AsyncSession]
    __session_factory: async_sessionmaker

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        raise NotImplementedError

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
            logger.error(f"Database operation failed: {exc_value}")
            logger.debug(f"Exception type: {exc_type}")
            logger.debug("Traceback:", exc_info=(exc_type, exc_value, traceback))
        await self.close()
        self.session = None
