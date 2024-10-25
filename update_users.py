import asyncio
from datetime import datetime, date
from typing import Dict, List, Tuple

from src.config import client
from src.models import async_session, User

from sqlalchemy import select


async def get_users():
    async with async_session() as session:
        users = (await session.execute(select(User.id, User.folder).where(User.registration_date >= datetime.now().replace(hour=00, minute=00, second=00)))).all()
    return users


async def get_users_and_dialogs() -> Tuple[Dict[int, str], List[int]]:
    users_with_folder = await get_users()
    dialogs = [dialog async for dialog in client.get_dialogs(limit=1500)]

    #users_with_folder, dialogs = await asyncio.gather(users_with_folder_task, dialogs_task)
    #dialogs = [dialog async for dialog in dialogs]

    users_with_folder_dict = {user[0]: user[1] for user in users_with_folder}

    relevant_dialogs = []
    for dialog in dialogs:
        if dialog.chat.id in users_with_folder_dict:
            messages = client.get_chat_history(dialog.chat.id)
            messages = [message async for message in messages]  # Преобразование в список
            if messages and messages[-1].date.date() == datetime.now().date():
                relevant_dialogs.append(dialog.chat.id)

    return users_with_folder_dict, relevant_dialogs


async def update_users():
    users_with_folder_dict, relevant_dialogs = await get_users_and_dialogs()
    folder_counts = {"Нет папки": 0}

    for user_id in relevant_dialogs:
        if user_id in users_with_folder_dict:
            folder = users_with_folder_dict[user_id]
            if folder in folder_counts:
                folder_counts[folder] += 1
            else:
                folder_counts[folder] = 1
        else:
            folder_counts["Нет папки"] += 1

    for folder, count in folder_counts.items():
        print(f"{folder}: {count}")
    print(f'Всего: {len(relevant_dialogs)}')




