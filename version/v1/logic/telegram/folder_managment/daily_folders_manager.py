from datetime import date
from itertools import product
from typing import Callable, Literal

from pyrogram.raw.types import DialogFilter
from loguru import logger
from pyrogram import Client
from src.logic.telegram.folder_managment import (
    DailyFoldersManagerInterface,
    DialogManagerInterface,
    FolderUtilsInterface
    )
from src.utils.constants import FolderDay
from version.v1.schemas.managers_shifts import OutputShift
from version.v1.logic.telegram.tasks_mexin.daily_folders import DailyFoldersMexin


class DailyFoldersManager(DailyFoldersManagerInterface, DailyFoldersMexin):
    
    def __init__(
        self,
        client: Client,
        dialog_manager: DialogManagerInterface,
        folder_utils: FolderUtilsInterface
    ):
        self.client = client
        self.dialog_manager = dialog_manager
        self.folder_utils = folder_utils
    
    async def _get_daily_folders_titles(
        self,
        *,
        shift: OutputShift,
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
        folders_titles = {
            f'{folder_day} {manager.prefix_name}'
            for folder_day, manager in product(folders_days, shift.managers)
        }
        return folders_titles
    
    def _folders_filters(self, folders_titles: set[str]) -> Callable[[DialogFilter], bool]:
        def is_folder_title(folder: DialogFilter) -> bool:
            return hasattr(folder, 'title') and folder.title in folders_titles
        return is_folder_title
    
    async def get_daily_folders(self, shift: OutputShift) -> list[DialogFilter]:
        folders_titles = await self._get_daily_folders_titles(shift=shift)

        # Getting necessary folders
        folders = await self.dialog_manager.get_dialog_filters(
            self._folders_filters(folders_titles)
        )
        return folders
    
    async def get_today_folders(self, shift: OutputShift) -> list[DialogFilter]:
        managers_titles: set[str] = await self._get_daily_folders_titles(shift=shift, day='today')
        folders = await self.dialog_manager.get_dialog_filters(
            self._folders_filters(managers_titles)
        )
        return folders
