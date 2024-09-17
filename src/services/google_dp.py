import gspread_asyncio
from google.oauth2.service_account import Credentials
from sqlalchemy.dialects.postgresql import insert

from loguru import logger

from src.models import db
from src.constants import DATA_DIR


def get_creds():
    creds = Credentials.from_service_account_file(DATA_DIR / 'google_api.json')
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


class GoogleDP:

    cards_sheet_id = "1jHZGWFMA2egzZncy2UltTeRwy7cNBORsWZqzEydjNDg"

    @classmethod
    async def get_last_row(cls, worksheet,  column: int) -> int:
        column_values = await worksheet.col_values(column)
        return len(column_values) + 1

    @classmethod
    async def insert_cards_db(cls):
        agc = await agcm.authorize()
        google_sheet = await agc.open_by_key(cls.cards_sheet_id)
        worksheet = await google_sheet.get_worksheet(0)

        data = await worksheet.get('A2:B50')
        cards = {}
        print(data)
        for row in data:
            card = int(row[0])
            status = row[1]
            cards[card] = status
        print(cards)
        if cards:
            await db.insert_cards(cards=cards)

    @classmethod
    async def insert_card_google_sheet(cls, card: int, status: str):
        agc = await agcm.authorize()
        google_sheet = await agc.open_by_key(cls.cards_sheet_id)
        worksheet = await google_sheet.get_worksheet(0)

        cell = await worksheet.find(str(card))
        if cell:
            row = cell.row
            await worksheet.update_acell(f'B{row}', status)
            logger.info(f'Update status card - {card} - {status}')
        else:
            row = await cls.get_last_row(worksheet, 1)
            if row is not None:
                await worksheet.update_acell(f'A{row}', str(card))
                await worksheet.update_acell(f'B{row}', status)
            logger.info(f'Insert new card - {card} - {status}')
