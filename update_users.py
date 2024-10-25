from datetime import datetime, timedelta, date

from src.config import client
from src.models import async_session, User

from sqlalchemy import update, select


async def get_users():
    async with async_session() as session:
        users = (await session.execute(select(User.id, User.folder).where(User.folder.is_(None)))).scalars().all()
    return users


async def update_user(id_: int):
    async with async_session() as session:
        await session.execute(update(User).values(registration_date=User.registration_date - timedelta(days=1)))
        await session.commit()


async def update_users():
    users_with_folder = await get_users()
    count = 0
    users = []
    async for dialog in client.get_dialogs():
        #if dialog.chat.id in users_id:
        messages = [message async for message in client.get_chat_history(dialog.chat.id)]
        if messages[-1].date.date() == date(2024, 10, 25):
            users.append(dialog.chat.id)
            count += 1


