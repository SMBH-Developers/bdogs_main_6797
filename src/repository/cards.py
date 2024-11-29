from abc import ABC, abstractmethod
from typing import Optional
from .base import BaseRepositoryInterface, Model, InputSchema, OutputSchema
from src.logic.google.google_sheet import GoogleSheetInterface


class CardRepositoryInterface(BaseRepositoryInterface[Model, InputSchema, OutputSchema], ABC):
    
    @abstractmethod
    async def insert_cards_db(self, google_sheet: GoogleSheetInterface) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def fetch_one(self, card: int, status: str) -> Optional[OutputSchema]:
        raise NotImplementedError
