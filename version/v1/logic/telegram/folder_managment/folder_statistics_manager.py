from src.logic.telegram.folder_managment import (
    FolderStatisticsInterface,
    DailyFoldersManagerInterface,
    FolderUtilsInterface
)
from schemas.telegram.folders import FoldersCategoryStat, FolderStat
from pyrogram import Client
from loguru import logger


class FolderStatistics(FolderStatisticsInterface[FoldersCategoryStat]):
    
    def __init__(
        self,
        daily_folders_manager: DailyFoldersManagerInterface,
        folder_utils: FolderUtilsInterface
    ):
        self.daily_folders_manager = daily_folders_manager
        self.folder_utils = folder_utils
    
    async def get_existing_chats(self, client: Client) -> set[int]:
        return {
            dialog.chat.id
            async for dialog in client.get_dialogs()
        }
    
    async def get_folders_statistic(self, client: Client) -> list[FoldersCategoryStat]:
        logger.info('Function **get_folders_statistic** started')
        folders = await self.daily_folders_manager.get_daily_folders()
        existing_chats = await self.get_existing_chats(client=client)
        folders_stat = [
            FolderStat(
                folder.title,
                len(self.folder_utils.extract_ids_from_peers(folder.include_peers) & existing_chats)
            )
            for folder in folders
        ]

        # Gathering to categories
        folders_categories = {"Сегодня": [], 'База': []}
        for folder in folders_stat:
            folder_category = folder.folder_title.split()[0]
            folders_categories[folder_category].append(folder)
        categories_stat = [
            FoldersCategoryStat(folders_by_category) for folders_by_category in folders_categories.values()
        ]

        return categories_stat
