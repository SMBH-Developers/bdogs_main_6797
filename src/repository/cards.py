from abc import ABC, abstractmethod
from .base import BaseRepositoryInterface, Model, InputSchema, OutputSchema
from src.logic.google.google_sheet import GoogleSheetInterface


class CardRepositoryInterface(BaseRepositoryInterface[Model, InputSchema, OutputSchema], ABC):
    
    @abstractmethod
    async def insert_cards_db(self, google_sheet: GoogleSheetInterface) -> None:
        raise NotImplementedError
