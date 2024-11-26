from abc import ABC, abstractmethod
from typing import Optional, Sequence
from pyrogram.raw.types import DialogFilter
from pyrogram.raw.base import InputPeer
from pyrogram import Client


class FolderUtilsInterface(ABC):
    DEFAULT_START_ID = 10
    
    @abstractmethod
    async def users_to_peers(
        self,
        users_ids: Optional[Sequence[int]],
        *,
        ignore_peer_invalid: bool = False
    ) -> Optional[list[InputPeer]]:
        raise NotImplementedError

    @abstractmethod
    def group_folders(self, folders: list[DialogFilter]) -> dict[str, list[DialogFilter]]:
        raise NotImplementedError
    
    @abstractmethod
    def extract_ids_from_peers(self, peers: list[InputPeer]) -> set[int]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_default_users(
        self,
        client: Client,
        users: Optional[Sequence[int]] = tuple()
    ) -> list[InputPeer]:
        raise NotImplementedError

    @abstractmethod
    async def get_new_folder_id(
        self,
        client: Client,
        *,
        step_id: int = 1
    ) -> int:
        raise NotImplementedError
