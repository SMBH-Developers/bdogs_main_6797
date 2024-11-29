from typing import Optional, Sequence

from pyrogram.raw.types import DialogFilter, InputPeerUser
from pyrogram.raw.base import InputPeer
from pyrogram import Client, raw, errors

from src.logic.telegram.folder_managment import FolderUtilsInterface
from loguru import logger


class FolderUtils(FolderUtilsInterface):
    
    async def users_to_peers(
        self,
        client: Client,
        users_ids: Optional[Sequence[int]],
        *,
        ignore_peer_invalid: bool = False
    ) -> Optional[list[InputPeer]]:
        peers = []
        for user_id in users_ids:
            try:
                peers.append(await client.resolve_peer(user_id))
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
                folders_list = grouped.setdefault(category, [])
                folders_list.append(folder)
            except (AttributeError, IndexError) as e:
                logger.warning(f"Некорректное название папки: {folder}, ошибка: {e}")
                continue
            
        for folders_list in grouped.values():
            folders_list.sort(key=lambda f: f.title.startswith('База'), reverse=True)
        
        return grouped
    
    
    def extract_ids_from_peers(self, peers: list[InputPeer]) -> set[int]:
        return {peer.user_id for peer in peers if isinstance(peer, InputPeerUser)}
    
    async def get_default_users(
        self,
        client: Client,
        users: Optional[Sequence[int]] = tuple()
    ) -> list[InputPeer]:
        users = await self.users_to_peers(client, users)
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