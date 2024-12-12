from abc import ABC
import inspect
from typing import Any, Callable, Generic, Type, TypeVar, Dict
from .daily_folders_manager import DailyFoldersManagerInterface
from .folder_statistics_manager import FolderStatisticsInterface
from .folder_utils_manager import FolderUtilsInterface
from .dialog_manager import DialogManagerInterface


T = TypeVar('T')
DailyInterface = TypeVar('DailyInterface', bound=DailyFoldersManagerInterface)
StatsInterface = TypeVar('StatsInterface', bound=FolderStatisticsInterface)
DialogInterface = TypeVar('DialogInterface', bound=DialogManagerInterface)
UtilsInterface = TypeVar('UtilsInterface', bound=FolderUtilsInterface)


class ManagerFactory(Generic[T]):    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
    
    def __call__(self) -> T:
        return self._factory()

class TelegramFolderManager(Generic[T]):
    def __init__(self, manager: Type[T], **dependencies: Any):
        self._factory: Callable[[], T] = self.__inject_dependencies(manager, dependencies)
    
    def __inject_dependencies(self, manager: Type[T], dependencies: Dict[str, Any]) -> Callable[[], T]:
        params = inspect.signature(manager).parameters
        deps = {
            name: dependency.manager() if isinstance(dependency, TelegramFolderManager) else dependency
            for name, dependency in dependencies.items()
            if name in params
        }
        return lambda: manager(**deps)
    
    @property
    def manager(self) -> ManagerFactory[T]:
        return ManagerFactory(self._factory)


class AllManagersFactoryInterface(
    Generic[
        DailyInterface, 
        StatsInterface, 
        DialogInterface, 
        UtilsInterface
    ],
    ABC
):
    daily: DailyInterface
    stats: StatsInterface
    dialog: DialogInterface
    utils: UtilsInterface
    
    def __init__(
        self,
        daily: Type[DailyInterface],
        stats: Type[StatsInterface],
        dialog: Type[DialogInterface],
        utils: Type[UtilsInterface],
        **dependencies: Any
    ):
        self._dialog = TelegramFolderManager[DialogInterface](
            dialog,
            **dependencies
        )
        self._utils = TelegramFolderManager[UtilsInterface](
            utils,
            **dependencies
        )
        self._daily = TelegramFolderManager[DailyInterface](
            daily,
            utils=self._utils,
            dialog=self._dialog,
            **dependencies
        )
        self._stats = TelegramFolderManager[StatsInterface](
            stats,
            daily=self._daily,
            utils=self._utils,
            **dependencies
        )
