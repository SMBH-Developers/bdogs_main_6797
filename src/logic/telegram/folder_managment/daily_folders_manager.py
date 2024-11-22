from abc import ABC, abstractmethod
from pyrogram.raw.types import DialogFilter


class DailyFoldersManagerInterface(ABC):
    
    @abstractmethod
    async def get_daily_folders(self) -> list[DialogFilter]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_today_folders(self) -> list[DialogFilter]:
        raise NotImplementedError
    
    @abstractmethod
    async def dispatch_users_via_daily_folders(self):
        raise NotImplementedError
