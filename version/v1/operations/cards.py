from pyrogram import Client
from pyrogram.types import Message

from src.logic.google.google_sheet import GoogleSheetInterface
from src.operations.base import BaseOperation
from version.v1.uow import UowV1
from version.v1.schemas import InputCard
from src.utils import extract_card_from_command


class CardOperation(BaseOperation):
    def __init__(
        self, 
        google_dp: GoogleSheetInterface,
        uow: UowV1,
        client: Client
    ):
        self.google_dp = google_dp
        self.uow = uow
        self.client = client
        
    async def white_card(self, message: Message):
        card = await extract_card_from_command(message)
        if card is None:
            return

        input_card = InputCard(card=card.replace(' ', ''), status='white')
        
        async with self.uow as session:
            is_exists = await session.card.fetch_one(input_card.card, status=input_card.status)
            
            if is_exists:
                await session.card.update(input_card.card, status=input_card.status)
            else:
                await session.card.insert_one(input_card)
                
            await session.commit()
        await self.google_dp.insert_card_google_sheet(input_card.card, input_card.status)
