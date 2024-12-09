from abc import ABC, abstractmethod

class DailyFoldersMexinInterface(ABC):
    @abstractmethod
    async def send_users_to_daily_folders(self) -> None:
        raise NotImplementedError
