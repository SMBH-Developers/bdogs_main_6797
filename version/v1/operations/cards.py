from pyrogram import Client
from pyrogram.types import Message
from loguru import logger

from src.logic.google.google_sheet import GoogleSheetInterface
from src.operations.base import BaseOperation
from version.v1.uow import UowV1
from version.v1.schemas import InputCard
from src.utils import extract_card_from_command





class WhiteCardOperation(BaseOperation):
    def __init__(
        self, 
        google_dp: GoogleSheetInterface,
        uow: UowV1,
        client: Client
    ):
        self.google_dp = google_dp
        self.uow = uow()
        self.client = client
        
    async def __call__(
        self, 
        message: Message, 
        status: str = 'white', 
        return_card: bool = False
    ) -> bool:
        card = await extract_card_from_command(message)
        if card is None:
            return False

        input_card = InputCard(card=card.replace(' ', ''), status=status)
        
        try:
            async with self.uow as session:
                is_exists = await session.card.fetch_one(card=input_card.card, status=input_card.status)
            
            if is_exists:
                await session.card.update_one(data=input_card, card=input_card.card, status=input_card.status)
            else:
                await session.card.insert_one(input_card)
                
            await session.commit()
        except Exception as e:
            logger.info(f'white_card not success: {e}')
            return False
        try:
            await self.google_dp.insert_card_google_sheet(input_card.card, input_card.status)
        except Exception as e:
            logger.info(f'insert_card_google_sheet not success: {e}')
            
            return False
        
        return card if return_card else True

class BlackCardOperation(WhiteCardOperation):
        
    async def __call__(self, message: Message, status: str = 'black') -> int:
        card = await super().__call__(message, status, return_card=True)
        count = 0
        async for search_message in self.client.search_global(card):
            try:
                if search_message.chat.type.PRIVATE and search_message.text != f'/black {card}' and search_message.text != f'/white {card}':
                    await search_message.delete()
                    count += 1
            except Exception as e:
                logger.error(f'ERROR DELETE CARD | {e}')

        return count