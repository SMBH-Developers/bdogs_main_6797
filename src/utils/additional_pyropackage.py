import asyncio
from dataclasses import dataclass
from typing import Callable, Optional, List

from loguru import logger
from pyrogram import raw
from pyrogram.raw.types import DialogFilter, DialogFilterDefault

from src.config import client


@dataclass
class FolderStat:
    folder_title: str
    peers_len: int


class Additional:

    @staticmethod
    async def users_to_peers(users_ids: list[int]):
        return [await client.resolve_peer(user_id) for user_id in users_ids]

    @staticmethod
    async def get_new_folder_id() -> int:
        folders = list(filter(
            lambda x: hasattr(x, 'id'),
            await client.invoke(raw.functions.messages.GetDialogFilters()))
        )
        return max(folders, key=lambda x: x.id).id + 1 if folders else 10

    @staticmethod
    async def _get_dialog_filters(
            folders_filter: Optional[Callable] = None
    ) -> List[DialogFilter | DialogFilterDefault]:

        folders = await client.invoke(raw.functions.messages.GetDialogFilters())
        updated_folders = [folder for folder in folders if not folders_filter or folders_filter(folder)]
        return updated_folders

    @classmethod
    async def create_dialog_filter(cls, title: str, *, users: list[int] = ()) -> DialogFilter:
        users = await cls.users_to_peers(users)
        if len(users) == 0:
            client_id = (await client.get_me()).id
            users = [await client.resolve_peer(client_id)]

        folder_filters = DialogFilter(
            id=(await cls.get_new_folder_id()),
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

    @classmethod
    async def get_daily_folders(cls) -> list[DialogFilter]:
        folders_titles = cls._get_daily_folders_titles()

        # Getting necessary folders
        folders_filters = [lambda folder: hasattr(folder, 'title') and folder.title in folders_titles]
        folders = await cls._get_dialog_filters(lambda folder: any([filter_(folder) for filter_ in folders_filters]))
        return folders

    @classmethod
    def _get_daily_folders_titles(cls):
        folders_categories = ['Ю', 'К', 'Е']
        folders_days = ['Позавчера', 'Вчера', 'Сегодня']
        folders_titles = {f'{folder_day} {folder_category}' for folder_day in folders_days
                          for folder_category in folders_categories
                          }
        return folders_titles

    @staticmethod
    def _sort_daily_folders_by_title(folders: list[DialogFilter]):
        sorting_order = ["Позавчера", "Вчера", "Сегодня"]
        folders.sort(key=lambda folder: sorting_order.index(folder.title.split()[0]))

    @staticmethod
    async def _select_new_include_peers(folder_title: str,
                                  folders: list[DialogFilter],
                                  client_id: int
                                  ):
        folder_day = folder_title.split()[0]
        if folder_day == "Сегодня":
            return raw.core.List([await client.resolve_peer(client_id)])
        # Если folder=Вчера, то берёт из Сегодня; Если folder=Позавчера, то берёт из Вчера
        necessary_folder_title = {"Вчера": "Сегодня", "Позавчера": "Вчера"}[folder_day] + f' {folder_title[-1]}'
        for folder in folders:
            if folder.title == necessary_folder_title:
                return folder.include_peers
        raise ValueError(f"Necessary directory is not found: <{necessary_folder_title}>")

    @classmethod
    async def add_user_to_folder(cls, folder_title: str, user_id: int):
        peer = await client.resolve_peer(user_id)
        folders = await cls._get_dialog_filters(lambda f: hasattr(f, 'title') and f.title == folder_title)
        if not folders:
            await cls.create_dialog_filter(folder_title, users=[user_id])
        else:
            folder = folders[0]
            if len(folder.include_peers) == 200:
                logger.info(f"{folder_title} has limit peers. So user [{user_id}] wasn't add to folder")
                return
            folder.include_peers.append(peer)
            await client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder.id, filter=folder))

    @classmethod
    async def get_today_folders(cls) -> list[DialogFilter]:
        titles = [f'Сегодня {category}' for category in "ЮКЕ"]
        folders = await cls._get_dialog_filters(lambda folder: hasattr(folder, 'title') and folder.title in titles)
        return folders

    @classmethod
    async def get_all_users_folder(cls):
        # Getting necessary folders
        folders = await cls.get_daily_folders()
        folders_titles = set(folder.title for folder in folders)

        # Creating non existing folders
        non_existing_folders_titles = cls._get_daily_folders_titles() - folders_titles
        print(f'non_existing_folders_titles: {non_existing_folders_titles}')
        folders.extend([await cls.create_dialog_filter(title) for title in non_existing_folders_titles])

        cls._sort_daily_folders_by_title(folders)
        # Вчера -> Позавчера; Сегодня -> Вчера; Сегодня -> []
        client_id = (await client.get_me()).id
        folders = [(folder, await cls._select_new_include_peers(folder.title, folders, client_id)) for folder in folders]
        for folder, new_included_peers in folders:
            folder.include_peers = new_included_peers
            await client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder.id, filter=folder))

    @classmethod
    async def get_folders_statistic(cls) -> list[FolderStat]:
        folders = await cls.get_daily_folders()
        folders_stat = [FolderStat(folder.title, len(folder.include_peers)) for folder in folders]
        return folders_stat

