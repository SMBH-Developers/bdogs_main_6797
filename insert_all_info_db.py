import asyncio
import json
from typing import Dict
from datetime import datetime, date

from sqlalchemy import insert

from src.database import User, Card, Shift, async_session


async def insert_users(users: Dict[int, datetime]):
    async with async_session() as session:
        for user_id, registration_date in users.items():
            await session.execute(insert(User).values(id=int(user_id), registration_date=datetime.fromisoformat(registration_date)))
        await session.commit()


async def insert_cards(cards: Dict[int, str]):
    async with async_session() as session:
        for card, status in cards.items():
            await session.execute(insert(Card).values(card=int(card), status=status))
        await session.commit()


async def insert_shifts(shifts: Dict[str, date]):
    async with async_session() as session:
        for managers, date_shift in shifts.items():
            await session.execute(insert(Shift).values(managers=managers, date=date.fromisoformat(date_shift)))
        await session.commit()


async def insert_all_info():
    with open('all_information.json', 'r', encoding='utf-8') as f:
        info = json.load(f)

    await insert_users(info['users'])
    await insert_cards(info['cards'])
    await insert_shifts(info['shifts'])

    print('Готово')


asyncio.run(insert_all_info())
