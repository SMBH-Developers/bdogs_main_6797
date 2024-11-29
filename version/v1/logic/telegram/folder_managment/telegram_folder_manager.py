from src.logic.telegram.folder_managment import AllManagersFactoryInterface
from .daily_folders_manager import DailyFoldersManager
from .folder_statistics_manager import FolderStatistics
from .dialog_manager import DialogManager
from .folder_utils_manager import FolderUtils


class AllManagersFactory(
    AllManagersFactoryInterface[
        DailyFoldersManager, 
        FolderStatistics, 
        DialogManager, 
        FolderUtils
    ]
):

    @property
    def daily(self) -> DailyFoldersManager:
        return self._daily.manager()
    
    @property
    def stats(self) -> FolderStatistics:
        return self._stats.manager()
    
    @property
    def dialog(self) -> DialogManager:
        return self._dialog.manager()
    
    @property
    def utils(self) -> FolderUtils:
        return self._utils.manager()
