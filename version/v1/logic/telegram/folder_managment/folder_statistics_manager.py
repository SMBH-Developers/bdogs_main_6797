from pyrogram import Client
from loguru import logger

from version.v1.schemas.telegram.folders import FoldersCategoryStat, FolderStat
from src.logic.telegram.folder_managment import (
    FolderStatisticsInterface,
    DailyFoldersManagerInterface,
    FolderUtilsInterface
)

from version.v1.logic.telegram.tasks_mexin.statistics import StatisticsMexin

class FolderStatistics(FolderStatisticsInterface[FoldersCategoryStat], StatisticsMexin):
    
    def __init__(
        self,
        daily_folders_manager: DailyFoldersManagerInterface,
        folder_utils: FolderUtilsInterface,
        client: Client
    ):
        self.daily_folders_manager = daily_folders_manager
        self.folder_utils = folder_utils
        self.client = client
    
    async def get_existing_chats(self) -> set[int]:
        return {
            dialog.chat.id
            async for dialog in self.client.get_dialogs()
        }
    
    async def get_folders_statistic(self, shift: 'OutputShift') -> list[FoldersCategoryStat]:
        logger.info('Function **get_folders_statistic** started')
        folders = await self.daily_folders_manager.get_daily_folders(shift=shift)
        existing_chats = await self.get_existing_chats()
        folders_stat = [
            FolderStat(
                folder_title=folder.title,
                peers_len=len(self.folder_utils.extract_ids_from_peers(folder.include_peers) & existing_chats)
            )
            for folder in folders
        ]

        # Gathering to categories
        folders_categories = {"Сегодня": [], 'База': []}
        for folder in folders_stat:
            folder_category = folder.folder_title.split()[0]
            folders_categories[folder_category].append(folder)
        categories_stat = [
            FoldersCategoryStat(folders_stat=folders_by_category)
            for folders_by_category in folders_categories.values()
        ]

        return categories_stat
