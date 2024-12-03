from typing import TypeVar, Generic, Type, Optional, Union
from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.database._models import Base
from sqlalchemy.ext.asyncio import AsyncSession


Model = TypeVar("Model", bound=Base)
InputSchema = TypeVar("InputSchema", bound=BaseModel)
OutputSchema = TypeVar("OutputSchema", bound=BaseModel)


class BaseRepositoryInterface(Generic[Model, InputSchema, OutputSchema], ABC):
    _model: Type[Model]
    _output_schema: Type[OutputSchema]
    _input_schema: Type[InputSchema]

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def fetch_one(self, **filters) -> Optional[OutputSchema]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_all(
        self, offset: int = 0, limit: int = 1000, **filters
    ) -> Optional[list[OutputSchema]]:
        raise NotImplementedError

    @abstractmethod
    async def insert_one(self, data: InputSchema) -> OutputSchema:
        raise NotImplementedError

    @abstractmethod
    async def insert_bulk(self, data: list[Union[InputSchema, dict]]) -> list[OutputSchema]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *, data: InputSchema, **filters) -> OutputSchema:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *, strong: bool = False, **filters) -> None:
        raise NotImplementedError
