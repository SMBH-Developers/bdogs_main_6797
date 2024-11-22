from abc import ABC, abstractmethod
from typing import List
from pyrogram.raw.types import DialogFilter, DialogFilterDefault

class TelegramFolderManagerInterface(ABC):
    
    @abstractmethod
    async def get_new_folder_id(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def add_user_to_folder(self, folder_title: str, user_id: int) -> None:
        raise NotImplementedError
