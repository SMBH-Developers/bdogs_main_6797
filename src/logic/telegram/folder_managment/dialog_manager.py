from abc import ABC, abstractmethod
from typing import Any, Callable, List
from pyrogram.raw.types import DialogFilter, DialogFilterDefault


class DialogManagerInterface(ABC):
    
    @abstractmethod
    async def get_dialog_filters(self, filter_func: Callable[[Any], bool]) -> List[DialogFilter | DialogFilterDefault]:
        raise NotImplementedError
    
    @abstractmethod
    async def create_dialog_filter(self, title: str, *, users: list[int] = ()) -> DialogFilter:
        raise NotImplementedError

