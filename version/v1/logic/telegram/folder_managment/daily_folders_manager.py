from datetime import date
from itertools import product
from typing import Callable, Literal

from pyrogram.raw.types import DialogFilter
from loguru import logger
from pyrogram import raw, errors
from pyrogram import Client
from src.logic.telegram.folder_managment import (
    DailyFoldersManagerInterface,
    DialogManagerInterface,
    FolderUtilsInterface
    )
from src.utils.constants import FolderDay
from version.v1.uow import UowV1
from version.v1.schemas.managers_shifts import OutputShift


class DailyFoldersManager(DailyFoldersManagerInterface):
    
    def __init__(
        self,
        client: Client,
        uow: UowV1,
        dialog_manager: DialogManagerInterface,
        folder_utils: FolderUtilsInterface
    ):
        self.client = client
        self.uow = uow
        self.dialog_manager = dialog_manager
        self.folder_utils = folder_utils
    
    async def _get_daily_folders_titles(
        self,
        *,
        day: Literal['today', 'base', 'all'] = 'all'
    ) -> set[str]:
        '''
        Returns:
            {
                'Сегодня Ан', 'Сегодня Ве', 'Сегодня Ка', 'Сегодня Ек', 'Сегодня Ек2',
                'Сегодня Эл', 'Сегодня Та', 'База Ан', 'База Ве', 'База Ка', 'База Ек',
                'База Ек2', 'База Эл', 'База Та'
            }
        '''
        folders_days = FolderDay[day].value
        async with self.uow as session:
            shift: OutputShift = await session.shift.fetch_one(
                date_=date.today(),
                is_deleted=False
            )
            await session.commit()
                
            folders_titles = {
                f'{folder_day} {manager.prefix_name}'
                for folder_day, manager in product(folders_days, shift.managers)
        }
        return folders_titles
    
    def _folders_filters(self, folders_titles: set[str]) -> Callable[[DialogFilter], bool]:
        def is_folder_title(folder: DialogFilter) -> bool:
            return hasattr(folder, 'title') and folder.title in folders_titles
        return is_folder_title
    
    async def get_daily_folders(self) -> list[DialogFilter]:
        folders_titles = await self._get_daily_folders_titles()

        # Getting necessary folders
        folders = await self.dialog_manager.get_dialog_filters(
            self.client,
            self._folders_filters(folders_titles)
        )
        return folders
    
    async def get_today_folders(self) -> list[DialogFilter]:
        managers_titles: set[str] = await self._get_daily_folders_titles(day='today')
        folders = await self.dialog_manager.get_dialog_filters(
            self.client,
            self._folders_filters(managers_titles)
        )
        return folders
    
    
    async def send_users_to_daily_folders(self):
        with logger.catch():
            logger.info('Function **dispatch_users_via_daily_folders** started')
            # Getting necessary folders
            folders = await self.get_daily_folders()
            logger.info(f'FOLDERS | get_daily_folders  -  {folders}')
            folders_titles = set(folder.title for folder in folders)
            logger.info(f'FOLDERS | folders title  -  {folders}')

            # Creating non existing folders
            non_existing_folders_titles = await self._get_daily_folders_titles() - folders_titles
            logger.info(f'FOLDERS | non existing folders titles  -  {folders}')
            folders.extend(
                await self.dialog_manager.create_dialog_filter(title)
                for title in non_existing_folders_titles
            )

            grouped_folders = self.folder_utils.group_folders(folders)
            for category, category_folders in grouped_folders.items():
                # print(f'Папка - {category}\nСодержимое - {category_folders}')
                total_folder, today_folder = category_folders
                # print(f'База - {total_folder}\n\nСегодня - {today_folder}\n\n')

                today_folder: DialogFilter
                total_folder: DialogFilter
                general_set_today = today_folder.pinned_peers + today_folder.include_peers
                general_set_total = total_folder.pinned_peers + total_folder.include_peers

                free_places_total_count = 200 - len(general_set_total)
                logger.info(f'FOLDERS | Free places total count - {free_places_total_count}')
                if len(general_set_today) > free_places_total_count:
                    users_to_del_count = len(general_set_today) - free_places_total_count
                else:
                    users_to_del_count = 0
                logger.info(f'FOLDERS | Count users to delete - {users_to_del_count}')

                old_users_to_delete = await db.get_old_users(users_to_del_count, self.folder_utils.extract_ids_from_peers(general_set_total))

                logger.info(f'FOLDERS | Start exctract ids from peers')
                users = (
                    self.folder_utils.extract_ids_from_peers(general_set_total) |
                    self.folder_utils.extract_ids_from_peers(general_set_today)
                ) - set(old_users_to_delete)
                logger.info(f'FOLDERS | End exctract ids from peers')
                total_folder.include_peers = raw.core.List(await self.folder_utils.users_to_peers(users, ignore_peer_invalid=True))

                # **** Dont touch next
                # In the end we clear Today directory
                today_folder.include_peers = raw.core.List([await self.client.resolve_peer('me')])
                today_folder.pinned_peers = raw.core.List([])
                logger.info(f'FOLDERS | Clear Today folder')
                # Update today and total folders:
                logger.info(f'FOLDERS | Start insert users in folders - Today and Total')
                await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=today_folder.id, filter=today_folder))
                logger.info(f'FOLDERS | Inserted users in folder Today')
                await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=total_folder.id, filter=total_folder))
                logger.info(f'FOLDERS | Inserted users in folder Total')

