from src.uow.base import BaseUowInterface
from version.v1.repository import (
    UserRepository,
    CardRepository,
    ManagersRepository,
    ShiftsRepository
)
from src.database._engine import async_session


class BaseUow(
    BaseUowInterface[
        UserRepository,
        ShiftsRepository,
        CardRepository,
        ManagersRepository
    ]
):
    def __init__(self):
        self.__session_factory = async_session
        
    def __call__(self):
        '''
        Для создания объекта через фабрику
        '''
        return BaseUow()

    async def __aenter__(self):
        self.session = self.__session_factory()
        self.user = UserRepository(self.session)
        self.card = CardRepository(self.session)
        self.managers = ManagersRepository(self.session)
        self.shift = ShiftsRepository(self.session)
        return self
    
    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
        
    async def close(self):
        await self.session.close()
