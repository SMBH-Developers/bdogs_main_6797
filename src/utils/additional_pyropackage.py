from dataclasses import dataclass
from typing import Callable, Optional, List

from loguru import logger
from pyrogram import raw
from pyrogram.raw.types import DialogFilter, DialogFilterDefault, InputPeerUser
from pyrogram.raw.base import InputPeer

from src.config import client
from src.models import db


@dataclass
class FolderStat:
    folder_title: str
    peers_len: int

    def to_text(self) -> str:
        return f'{self.folder_title} - {self.peers_len}'


@dataclass
class FoldersCategoryStat:
    folders_stat: list[FolderStat]

    @property
    def total_count(self):
        return sum([folder_stat.peers_len for folder_stat in self.folders_stat])

    def to_text(self) -> str:
        stat = '\n'.join([folder_stat.to_text() for folder_stat in self.folders_stat])
        stat += f'\n\nВсего: {self.total_count}'

        return stat


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
        print(updated_folders)
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
        folders_titles = await cls._get_daily_folders_titles()

        # Getting necessary folders
        folders_filters = [lambda folder: hasattr(folder, 'title') and folder.title in folders_titles]
        folders = await cls._get_dialog_filters(lambda folder: any([filter_(folder) for filter_ in folders_filters]))
        return folders

    @classmethod
    async def _get_daily_folders_titles(cls):
        #folders_categories = list("АЮКЕС")
        folders_categories = ['Ек', 'Ка', 'Су', 'Ди', 'Ек2']
        folders_days = ['Сегодня', 'База']
        folders_titles = {f'{folder_day} {folder_category}' for folder_day in folders_days
                          for folder_category in folders_categories
                          }
        return folders_titles

    @staticmethod
    def _sort_daily_folders_by_title(folders: list[DialogFilter]):
        sorting_order = ["База", "Сегодня"]
        folders.sort(key=lambda folder: sorting_order.index(folder.title.split()[0]))

    @staticmethod
    async def _select_folder_of_new_peers(folder_title: str,
                                          folders: list[DialogFilter],
                                          client_id: int
                                          ) -> tuple[list, list]:
        folder_day = folder_title.split()[0]
        if folder_day == "Сегодня":
            return raw.core.List([await client.resolve_peer(client_id)]), raw.core.List([])

        # Если folder=База, то берёт из Сегодня
        necessary_folder_title = {"База": "Сегодня"}[folder_day] + f' {folder_title[-3:].replace(" ", "")}'
        for folder in folders:
            if folder.title == necessary_folder_title:
                return folder.include_peers, folder.pinned_peers
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
        managers_today = await db.get_managers_today()
        managers = managers_today if managers_today is not None else ['Ек', 'Ка', 'Су', 'Ди', 'Ек2']
        titles = [f'Сегодня {category}' for category in managers]
        folders = await cls._get_dialog_filters(lambda folder: hasattr(folder, 'title') and folder.title in titles)
        return folders

    @classmethod
    async def dispatch_users_via_daily_folders(cls):
        logger.info('Function **dispatch_users_via_daily_folders** started')
        # Getting necessary folders
        folders = await cls.get_daily_folders()
        folders_titles = set(folder.title for folder in folders)

        # Creating non existing folders
        non_existing_folders_titles = await cls._get_daily_folders_titles() - folders_titles
        folders.extend([await cls.create_dialog_filter(title) for title in non_existing_folders_titles])

        cls._sort_daily_folders_by_title(folders)
        # База -> Все чаты; Сегодня -> База
        client_id = (await client.get_me()).id
        folders = [(folder, await cls._select_folder_of_new_peers(folder.title, folders, client_id)) for folder in folders]
        for folder, peers_tuple in folders:
            folder.include_peers, folder.pinned_peers = peers_tuple
            await client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder.id, filter=folder))

    @classmethod
    def extract_ids_from_peers(cls, peers: list[InputPeer]) -> list[int]:
        return [peer.user_id for peer in peers if isinstance(peer, InputPeerUser)]

    @classmethod
    async def get_folders_statistic(cls) -> list[FoldersCategoryStat]:
        logger.info('Function **get_folders_statistic** started')
        folders = await cls.get_daily_folders()
        folders_stat = [FolderStat(folder.title, len(set(cls.extract_ids_from_peers(folder.include_peers)) - set(cls.extract_ids_from_peers(folder.exclude_peers)))) for folder in folders]

        # Gathering to categories
        folders_categories = {"Сегодня": [], 'База': []}
        for folder in folders_stat:
            folder_category = folder.folder_title.split()[0]
            folders_categories[folder_category].append(folder)
        categories_stat = [
            FoldersCategoryStat(folders_by_category) for folders_by_category in folders_categories.values()
        ]

        return categories_stat
