from abc import ABC, abstractmethod

class StatisticsMexinInterface(ABC):
    @abstractmethod
    async def get_folder_stats_today(self, users_with_folder: list['OutputUser'])-> str:
        raise NotImplementedError
