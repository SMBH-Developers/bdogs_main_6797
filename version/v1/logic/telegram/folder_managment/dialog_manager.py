from typing import Any, Callable, List, Optional

from pyrogram.raw.types import DialogFilter, DialogFilterDefault
from src.logic.telegram.folder_managment import DialogManagerInterface
from pyrogram import Client
from pyrogram import raw, errors


class DialogManager(DialogManagerInterface):
    
    async def get_dialog_filters(
        self,
        client: Client,
        filter_func: Optional[Callable[[Any], bool]] = None
    ) -> List[DialogFilter | DialogFilterDefault]:
        folders = await client.invoke(raw.functions.messages.GetDialogFilters())
        updated_folders = [
            folder for folder in folders
            if not filter_func or filter_func(folder)
        ]
        return updated_folders
    
    async def create_dialog_filter(
        self,
        client: Client,
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
        await client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder_filters.id, filter=folder_filters))
        return folder_filters