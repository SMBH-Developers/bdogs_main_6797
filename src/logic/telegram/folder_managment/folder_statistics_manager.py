from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel
from pyrogram import Client


OutputFoldersStatistic = TypeVar('OutputFoldersStatistic', bound=BaseModel)


class FolderStatisticsInterface(Generic[OutputFoldersStatistic], ABC):
    
    @abstractmethod
    async def get_existing_chats(self, client: Client) -> set[int]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_folders_statistic(self) -> list[OutputFoldersStatistic]:
        raise NotImplementedError
