from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

from src.logic.telegram.tasks_mexin.statistics import StatisticsMexinInterface

OutputFoldersStatistic = TypeVar('OutputFoldersStatistic', bound=BaseModel)


class FolderStatisticsInterface(Generic[OutputFoldersStatistic], StatisticsMexinInterface, ABC):
    
    @abstractmethod
    async def get_existing_chats(self) -> set[int]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_folders_statistic(self) -> list[OutputFoldersStatistic]:
        raise NotImplementedError
