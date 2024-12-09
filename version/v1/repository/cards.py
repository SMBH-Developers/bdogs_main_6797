from loguru import logger
from sqlalchemy import delete, insert
from src.database._models import Card
from src.logic.google.google_sheet import GoogleSheetInterface
from src.repository.cards import CardRepositoryInterface
from .base import BaseRepository
from version.v1.schemas import InputCard, OutputCard, InputCardSheet


class CardRepository(BaseRepository[Card, InputCard, OutputCard]):
    '''Является реализацией интерфейса CardRepositoryInterface'''
    _model = Card
    _output_schema = OutputCard
    _input_schema = InputCard
    
    async def insert_cards_db(self, google_sheet: GoogleSheetInterface) -> None: # TODO: Возможно не нужно будет использовать
        logger.info("GoogleSheet: Started function <insert_cards_db>")
        worksheet = await google_sheet.get_worksheet()
        
        data = await worksheet.get('A2:B50')
        cards = InputCardSheet.model_validate(
            dict(
                cards=data
            )   
        )
        if cards.cards:
            try:
                await self.session.execute(delete(self._model))
                await self.session.execute(insert(self._model).values(**cards.cards))
            except Exception as e:
                logger.error(f"GoogleSheet: Error inserting cards to database: {e}")