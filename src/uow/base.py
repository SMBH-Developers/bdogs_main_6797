from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.repository.base import BaseRepositoryInterface
from src.repository.cards import CardRepositoryInterface


UserRepository = TypeVar("UserRepository", bound=BaseRepositoryInterface)
ShiftRepository = TypeVar("ShiftRepository", bound=BaseRepositoryInterface)
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
        await self.close()
        self.session = None
