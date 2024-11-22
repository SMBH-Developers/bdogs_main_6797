from abc import ABC, abstractmethod
from gspread_asyncio import AsyncioGspreadWorksheet

class GoogleSheetInterface(ABC):
    
    @abstractmethod
    async def get_last_row(self, worksheet,  column: int) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def get_worksheet(self) -> AsyncioGspreadWorksheet:
        raise NotImplementedError
    
    @abstractmethod
    async def insert_card_google_sheet(self, card: int, status: str) -> None:
        raise NotImplementedError
