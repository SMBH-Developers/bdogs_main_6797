from typing import Optional, Sequence

from pyrogram.raw.types import DialogFilter, InputPeerUser
from pyrogram.raw.base import InputPeer
from pyrogram import Client, raw, errors

from src.logic.telegram.folder_managment import FolderUtilsInterface
from loguru import logger


class FolderUtils(FolderUtilsInterface):
    
    
    def __init__(self, client: Client):
        self.client = client
    
    async def users_to_peers(
        self,
        users_ids: Optional[Sequence[int]],
        *,
        ignore_peer_invalid: bool = False
    ) -> Optional[list[InputPeer]]:
        peers = []
        for user_id in users_ids:
            try:
                peers.append(await self.client.resolve_peer(user_id))
            except errors.PeerIdInvalid:
                if not ignore_peer_invalid:
                    raise
        return peers
    
   
    def group_folders(self, folders: Sequence[DialogFilter]) -> dict[str, list[DialogFilter]]:
        """
        Группировка папок по категориям с сортировкой (Сегодня, База).
        """
        if not folders:
            return {}

        grouped = {}
        for folder in folders:
            try:
                category = folder.title.split()[-1]
                if category not in grouped:
                    grouped[category] = []
                
                logger.debug(f"Adding '{folder.title}' to '{category}', current folders: {[f.title for f in grouped[category]]}")
                grouped[category].append(folder)
                logger.debug(f"After adding: {category} has {[f.title for f in grouped[category]]}")
                
            except (AttributeError, IndexError) as e:
                logger.error(f"Failed to process folder: {folder.title if hasattr(folder, 'title') else folder}")
                continue
        
        return grouped
    
    
    def extract_ids_from_peers(self, peers: list[InputPeer]) -> set[int]:
        return {peer.user_id for peer in peers if isinstance(peer, InputPeerUser)}
    
    async def get_default_users(
        self,
        users: Optional[Sequence[int]] = tuple()
    ) -> list[InputPeer]:
        users = await self.users_to_peers(users)
        if not users:
            client_id = (await self.client.get_me()).id
            users = [await self.client.resolve_peer(client_id)]
        return users
    
    async def get_new_folder_id(
        self,
        *,
        step_id: int = 1
    ) -> int:
        try:
            folders = await self.client.invoke(raw.functions.messages.GetDialogFilters())
            valid_ids = [
                folder.id 
                for folder in folders 
                if hasattr(folder, 'id')
            ]
            return max(valid_ids, default=self.DEFAULT_START_ID - step_id) + step_id
        except Exception as e:
            logger.error(f"Error getting folder ID: {e}")
            return self.DEFAULT_START_ID