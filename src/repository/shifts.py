from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
from .base import BaseRepositoryInterface, Model, InputSchema, OutputSchema


class ShiftRepositoryInterface(BaseRepositoryInterface[Model, InputSchema, OutputSchema], ABC):
    
    @abstractmethod
    async def fetch_one(self, date_: date, **filters) -> Optional[OutputSchema]:
        raise NotImplementedError
    
    @abstractmethod
    async def insert_bulk(self, data: list[dict]) -> None:
        raise NotImplementedError
