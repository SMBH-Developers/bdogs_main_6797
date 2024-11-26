from schemas.telegram.folders import FoldersCategoryStat

class FolderStatistics:
    @classmethod
    async def get_existing_chats(cls):
        ...
    
    @classmethod
    async def get_folders_statistic(cls) -> list[FoldersCategoryStat]:
        ...
