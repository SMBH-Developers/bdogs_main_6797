from typing import TypeVar, Generic, Optional
from abc import ABC, abstractmethod

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.base import BaseRepositoryInterface


UserRepository = TypeVar("UserRepository", bound=BaseRepositoryInterface)
ShiftRepository = TypeVar("ShiftRepository", bound=BaseRepositoryInterface)
CardRepository = TypeVar("CardRepository", bound=BaseRepositoryInterface)
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

    # async def __aenter__(self):
    #     self.session = self.__session_factory()
    #     self.user = UserRepository(self.session)
    #     self.shift = ShiftRepository(self.session)
    #     self.card = CardRepository(self.session)
    #     self.managers = ManagersRepository(self.session)
    #
    # async def __aexit__(self):
    #     await self.rollback()
    #     await self.close()
