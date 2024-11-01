from datetime import datetime
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

    users_with_folder_dict = {user[0]: user[1] for user in users_with_folder}

    relevant_dialogs = []
    for dialog in dialogs:
        if dialog.chat.id in users_with_folder_dict:
            messages = client.get_chat_history(dialog.chat.id)
            messages = [message async for message in messages]
            if messages and messages[-1].date.date() == datetime.now().date():
                relevant_dialogs.append(dialog.chat.id)

    return users_with_folder_dict, relevant_dialogs


async def get_folder_stats_today():
    users_with_folder_dict, relevant_dialogs = await get_users_and_dialogs()
    folder_counts = {"Нет папки": 0}

    for user_id in relevant_dialogs:
        folder = users_with_folder_dict.get(user_id)
        if folder is None:
            folder_counts["Нет папки"] += 1
        else:
            if folder in folder_counts:
                folder_counts[folder] += 1
            else:
                folder_counts[folder] = 1

    # Формирование результата
    result = ""
    result += "Сегодня Су: {}\n".format(folder_counts.get("Су", 0))
    result += "Сегодня Ек2: {}\n".format(folder_counts.get("Ек2", 0))
    result += "Сегодня Ан: {}\n".format(folder_counts.get("Ан", 0))
    result += "Сегодня Та: {}\n".format(folder_counts.get("Та", 0))
    result += "Сегодня Ве: {}\n\n".format(folder_counts.get("Ве", 0))

    total_in_folders = sum(folder_counts.values()) - folder_counts["Нет папки"]
    result += "Всего в папках: {}\n\n".format(total_in_folders)

    result += "Пользователей без папки: {}\n\n".format(folder_counts["Нет папки"])
    result += "Всего за сегодня: {}".format(len(relevant_dialogs))

    return result
