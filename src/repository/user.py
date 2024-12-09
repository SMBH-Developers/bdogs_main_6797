from abc import ABC, abstractmethod
from .base import BaseRepositoryInterface, Model, InputSchema, OutputSchema


class UserRepositoryInterface(BaseRepositoryInterface[Model, InputSchema, OutputSchema], ABC):

    @abstractmethod
    async def get_count_without_folder(self) -> int:
        raise NotImplementedError
