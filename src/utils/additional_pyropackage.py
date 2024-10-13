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
        managers = await db.get_managers_today()
        folders_categories = managers.split(" ") if managers is not None else ['Су', 'Ек2', 'Ка', 'Ек', 'Ан', 'Эл', 'Та', 'Ве', 'Стас']
        folders_days = ['Сегодня', 'База']
        folders_titles = {f'{folder_day} {folder_category}' for folder_day in folders_days
                          for folder_category in folders_categories
                          }
        return folders_titles

    @staticmethod
    def _group_folders(folders: list[DialogFilter]) -> dict[str, list[DialogFilter]]:
        # Grouping
        grouped_folders = {}
        for folder in folders:
            category = folder.title.split()[-1]
            if category not in grouped_folders:
                grouped_folders[category] = []
            grouped_folders[category].append(folder)

        # Sorting
        for key in grouped_folders:
            grouped_folders[key].sort(key=lambda folder: folder.title.split()[0] == 'База', reverse=True)  # Order: Сегодня, База

        return grouped_folders

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
        managers = managers_today.split(" ") if managers_today is not None else ['Су', 'Ек2', 'Ка', 'Ек', 'Ан', 'Эл', 'Та', 'Ве', 'Стас']
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

        client_id = (await client.get_me()).id
        grouped_folders = cls._group_folders(folders)
        for category, category_folders in grouped_folders.items():
            # print(f'Папка - {category}\nСодержимое - {category_folders}')
            total_folder, today_folder = category_folders
            # print(f'База - {total_folder}\n\nСегодня - {today_folder}\n\n')

            today_folder: DialogFilter
            total_folder: DialogFilter
            general_set_today = today_folder.pinned_peers + today_folder.include_peers
            general_set_total = total_folder.pinned_peers + total_folder.include_peers

            free_places_total_count = 200 - len(general_set_total)
            if len(general_set_today) > free_places_total_count:
                users_to_del_count = len(general_set_today) - free_places_total_count
            else:
                users_to_del_count = 0
            old_users_to_delete = await db.get_old_users(users_to_del_count, cls.extract_ids_from_peers(general_set_total))
            
            users = (cls.extract_ids_from_peers(general_set_total) | cls.extract_ids_from_peers(general_set_today)) - set(old_users_to_delete) - {5493547563}
            total_folder.include_peers = raw.core.List([await client.resolve_peer(user) for user in users])

            # **** Dont touch next
            # In the end we clear Today directory
            today_folder.include_peers = raw.core.List([await client.resolve_peer(client_id)])
            today_folder.pinned_peers = raw.core.List([])

            # Update today and total folders:
            await client.invoke(raw.functions.messages.UpdateDialogFilter(id=today_folder.id, filter=today_folder))
            await client.invoke(raw.functions.messages.UpdateDialogFilter(id=total_folder.id, filter=total_folder))

    @classmethod
    def extract_ids_from_peers(cls, peers: list[InputPeer]) -> set[int]:
        return set(peer.user_id for peer in peers if isinstance(peer, InputPeerUser))

    @classmethod
    async def get_existing_chats(cls):
        existing_chats = []
        async for dialog in client.get_dialogs():
            existing_chats.append(dialog.chat.id)
        return set(existing_chats)

    @classmethod
    async def get_folders_statistic(cls) -> list[FoldersCategoryStat]:
        logger.info('Function **get_folders_statistic** started')
        folders = await cls.get_daily_folders()
        existing_chats = await cls.get_existing_chats()
        folders_stat = [FolderStat(folder.title, len((set(cls.extract_ids_from_peers(folder.include_peers)) & existing_chats))) for folder in folders]

        # Gathering to categories
        folders_categories = {"Сегодня": [], 'База': []}
        for folder in folders_stat:
            folder_category = folder.folder_title.split()[0]
            folders_categories[folder_category].append(folder)
        categories_stat = [
            FoldersCategoryStat(folders_by_category) for folders_by_category in folders_categories.values()
        ]

        return categories_stat
