from typing import Optional, Sequence

from pyrogram.raw.types import DialogFilter
from pyrogram.raw.base import InputPeer
from pyrogram import Client, raw

from src.logic.telegram.folder_managment import FolderUtilsInterface
from loguru import logger


class FolderUtils(FolderUtilsInterface):
    
    async def users_to_peers(
        self,
        users_ids: Optional[Sequence[int]],
        *,
        ignore_peer_invalid: bool = False
    ) -> Optional[list[InputPeer]]:
        ...
    
    @staticmethod
    def group_folders(folders: list[DialogFilter]) -> dict[str, list[DialogFilter]]:
        ...
    
    @classmethod
    def extract_ids_from_peers(cls, peers: list[InputPeer]) -> set[int]:
        ...
    
    async def get_default_users(
        self,
        client: Client,
        users: Optional[Sequence[int]] = tuple()
    ) -> list[InputPeer]:
        users = await self.users_to_peers(users)
        if not users:
            client_id = (await client.get_me()).id
            users = [await client.resolve_peer(client_id)]
        return users
    
    async def get_new_folder_id(
        self,
        client: Client,
        *,
        step_id: int = 1
    ) -> int:
        try:
            folders = await client.invoke(raw.functions.messages.GetDialogFilters())
            valid_ids = [
                folder.id 
                for folder in folders 
                if hasattr(folder, 'id')
            ]
            return max(valid_ids, default=self.DEFAULT_START_ID - step_id) + step_id
        except Exception as e:
            logger.error(f"Error getting folder ID: {e}")
            return self.DEFAULT_START_ID