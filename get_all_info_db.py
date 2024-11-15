import asyncio
import json
from typing import Dict
from datetime import date, datetime

from sqlalchemy import select

from src.database import Card, User, Shift, async_session


async def get_users() -> Dict[int, datetime]:  # return {id: datetime}
    users_dict: Dict = {}
    async with async_session() as session:
        users = (await session.execute(select(User))).scalars().all()

    for user in users:
        users_dict[user.id] = user.registration_date

    return users_dict


async def get_shifts() -> Dict[str, date]:  # return {'managers': date}
    shifts_dict: Dict = {}
    async with async_session() as session:
        shifts = (await session.execute(select(Shift))).scalars().all()

    for shift in shifts:
        shifts_dict[shift.managers] = shift.date

    return shifts_dict


async def get_cards() -> Dict[int, str]:  # return {number card: 'status'}
    cards_dict: Dict = {}
    async with async_session() as session:
        cards = (await session.execute(select(Card))).scalars().all()

    for card in cards:
        cards_dict[card.card] = card.status

    return cards_dict


async def write_all_information() -> None:
    cards = await get_cards()
    users = await get_users()
    shifts = await get_shifts()

    result = {'users': users, 'shifts': shifts, 'cards': cards}
    with open('all_information.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)


asyncio.run(write_all_information())
