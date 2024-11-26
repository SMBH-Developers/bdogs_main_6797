from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional
from pyrogram.raw.types import DialogFilter, DialogFilterDefault
from pyrogram import Client


class DialogManagerInterface(ABC):
    
    @abstractmethod
    async def get_dialog_filters(
        self,
        client: Client,
        filter_func: Optional[Callable[[Any], bool]] = None
    ) -> List[DialogFilter | DialogFilterDefault]:
        raise NotImplementedError
    
    @abstractmethod
    async def create_dialog_filter(
        self,
        client: Client,
        new_folder_id: int,
        title: str,
        users: list[int]
    ) -> DialogFilter:
        raise NotImplementedError

