from abc import ABC, abstractmethod
from pyrogram.raw.types import DialogFilter
from pyrogram.raw.base import InputPeer


class FolderUtilsInterface(ABC):
    
    @abstractmethod
    async def users_to_peers(
        self,
        users_ids: list[int] | set[int],
        *,
        ignore_peer_invalid: bool = False
    ) -> list[InputPeer]:
        raise NotImplementedError

    @abstractmethod
    def group_folders(self, folders: list[DialogFilter]) -> dict[str, list[DialogFilter]]:
        raise NotImplementedError
    
    @abstractmethod
    def extract_ids_from_peers(self, peers: list[InputPeer]) -> set[int]:
        raise NotImplementedError
    
