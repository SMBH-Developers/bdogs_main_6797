from typing import Optional
from abc import ABC, abstractmethod
from .base import BaseRepositoryInterface, Model, InputSchema, OutputSchema


class UserRepositoryInterface(BaseRepositoryInterface[Model, InputSchema, OutputSchema], ABC):

    @abstractmethod
    async def get_count_without_folder(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def fetch_all(self, *filters, offset: int = 0, limit: int = 1000) -> Optional[list[OutputSchema]]:
        raise NotImplementedError