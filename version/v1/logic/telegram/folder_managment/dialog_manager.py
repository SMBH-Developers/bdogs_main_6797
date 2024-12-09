from typing import Any, Callable, List, Optional

from pyrogram.raw.types import DialogFilter, DialogFilterDefault
from src.logic.telegram.folder_managment import DialogManagerInterface
from pyrogram import Client
from pyrogram import raw, errors
from loguru import logger


class DialogManager(DialogManagerInterface):
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_dialog_filters(
        self,
        filter_func: Optional[Callable[[Any], bool]] = None
    ) -> List[DialogFilter | DialogFilterDefault]:
        folders = await self.client.invoke(raw.functions.messages.GetDialogFilters())
        updated_folders = [
            folder for folder in folders
            if not filter_func or filter_func(folder)
        ]
        return updated_folders
    
    async def create_dialog_filter(
        self,
        new_folder_id: int,
        title: str,
        users: list[int]
    ) -> DialogFilter:

        folder_filters = DialogFilter(
            id=new_folder_id,
            title=title,
            pinned_peers=raw.core.List([]),
            include_peers=raw.core.List(users),
            exclude_peers=raw.core.List([]),
            contacts=False, non_contacts=False, groups=False, broadcasts=False,
            bots=False, exclude_muted=False, exclude_read=False, exclude_archived=True,
            emoticon=''
        )
        await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder_filters.id, filter=folder_filters))
        return folder_filters
    
    async def add_peer_to_filter(self, filter_title: str, peer_id: int) -> None:
        peer = await self.client.resolve_peer(peer_id)
        filters = await self.get_dialog_filters(
            lambda f: hasattr(f, 'title') and f.title == filter_title
        )
        
        if not filters:
            await self.create_dialog_filter(filter_title, users=[peer_id])
        else:
            dialog_filter = filters[0]
            if len(dialog_filter.include_peers) == 200:
                logger.info(f"{filter_title} has limit peers. So user [{peer_id}] wasn't add to filter")
                return
            dialog_filter.include_peers.append(peer)
            await self.client.invoke(
                raw.functions.messages.UpdateDialogFilter(
                    id=dialog_filter.id, 
                    filter=dialog_filter
                )
            )