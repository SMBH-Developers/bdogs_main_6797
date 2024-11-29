from abc import ABC, abstractmethod
from typing import Literal
from pyrogram.raw.types import DialogFilter


class DailyFoldersManagerInterface(ABC):
    
    @abstractmethod
    async def get_daily_folders(
        self,
        *,
        day: Literal['today', 'base', 'all'] = 'all'
    ) -> set[str]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_today_folders(self) -> list[DialogFilter]:
        raise NotImplementedError
    
    @abstractmethod
    async def send_users_to_daily_folders(self):
        raise NotImplementedError
