from typing import Callable

import gspread_asyncio
from gspread_asyncio import AsyncioGspreadWorksheet
from google.oauth2.service_account import Credentials
from loguru import logger


class GoogleSheet:
    
    def __init__(
        self,
        generate_creds: Callable[[], Credentials]
    ):
        self._agcm = gspread_asyncio.AsyncioGspreadClientManager(generate_creds)
        self.__cards_sheet_id = "1jHZGWFMA2egzZncy2UltTeRwy7cNBORsWZqzEydjNDg"
    
    async def get_last_row(self, worksheet,  column: int) -> int:
        try:
            column_values = await worksheet.col_values(column)
            return len(column_values) + 1
        except Exception as e:
            logger.error(f"GoogleSheet: Error getting last row with column {column}: {e}")
            raise e
    
    async def get_worksheet(self) -> AsyncioGspreadWorksheet:
        try:
            agc = await self._agcm.authorize()
            google_sheet = await agc.open_by_key(self.__cards_sheet_id)
            return await google_sheet.get_worksheet(0)
        except Exception as e:
            logger.error(f"GoogleSheet: Error opening google sheet: {e}")
            raise e
  
    async def insert_card_google_sheet(self, card: int, status: str) -> None:
        worksheet = await self.get_worksheet()

        cell = await worksheet.find(str(card))
        if cell:
            row = cell.row
            try:
                await worksheet.update_acell(f'B{row}', status)
                logger.info(f'Update status card - {card} - {status}')
            except Exception as e:
                logger.error(f"GoogleSheet: Error updating status card - {card} - {status}: {e}")
        else:
            row = await self.get_last_row(worksheet, 1)
            if row is not None:
                await worksheet.update_acell(f'A{row}', str(card))
                await worksheet.update_acell(f'B{row}', status)
            logger.info(f'Insert new card - {card} - {status}')

    # async def insert_cards_db(self):
    #     logger.info("GoogleSheet: Started function <insert_cards_db>")
    #     worksheet = await self.get_worksheet()
        
    #     data = await worksheet.get('A2:B50')
    #     cards = {}
    #     for row in data:
    #         card = int(row[0])
    #         status = row[1]
    #         cards[card] = status
            
    #     if cards:
    #         try:
    #             async with self.uow as session:
    #                 await session.card.insert_cards(cards=cards)
    #                 await session.commit()
    #         except Exception as e:
    #             logger.error(f"GoogleSheet: Error inserting cards to database: {e}")
        

