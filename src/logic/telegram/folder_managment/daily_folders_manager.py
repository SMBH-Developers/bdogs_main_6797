from abc import ABC, abstractmethod
from typing import Literal
from pyrogram.raw.types import DialogFilter

from src.logic.telegram.tasks_mexin.daily_folders import DailyFoldersMexinInterface


class DailyFoldersManagerInterface(ABC, DailyFoldersMexinInterface):
    
    @abstractmethod
    async def get_daily_folders(
        self,
        *,
        shift: 'OutputShift',
        day: Literal['today', 'base', 'all'] = 'all'
    ) -> set[str]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_today_folders(self, shift: 'OutputShift') -> list[DialogFilter]:
        raise NotImplementedError
