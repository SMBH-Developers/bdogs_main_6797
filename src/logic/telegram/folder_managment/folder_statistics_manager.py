from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

OutputFoldersStatistic = TypeVar('OutputFoldersStatistic', bound=BaseModel)


class FolderStatisticsInterface(Generic[OutputFoldersStatistic], ABC):
    
    @abstractmethod
    async def get_existing_chats(self) -> list[int]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_folders_statistic(self) -> list[OutputFoldersStatistic]:
        raise NotImplementedError
