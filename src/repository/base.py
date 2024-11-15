from typing import TypeVar, Generic, Type
from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.database._models import Base
from sqlalchemy.ext.asyncio import AsyncSession


Model = TypeVar('Model', bound=Base)
InputSchema = TypeVar('InputSchema', bound=BaseModel)
OutputSchema = TypeVar('OutputSchema', bound=BaseModel)


class BaseRepository(Generic[Model, InputSchema, OutputSchema], ABC):
    _model: Type[Model]
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def fetch_one(self, id_: int) -> OutputSchema:
        raise NotImplementedError

    @abstractmethod
    async def fetch_all(self) -> list[OutputSchema]:
        raise NotImplementedError
    
    @abstractmethod
    async def insert_one(self, data: InputSchema) -> OutputSchema:
        raise NotImplementedError
    
    @abstractmethod
    async def insert_bulk(self, data: list[InputSchema]) -> list[OutputSchema]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id_: int, data: InputSchema) -> OutputSchema:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id_: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_exists(self, id_: int) -> bool:
        raise NotImplementedError
