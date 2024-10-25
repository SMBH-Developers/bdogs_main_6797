from datetime import datetime, timedelta, date

from src.config import client
from src.models import async_session, User
from src.utils import Additional

from sqlalchemy import update, select


async def get_users():
    async with async_session() as session:
        users = (await session.execute(select(User.id, User.folder).where(User.registration_date >= datetime.now().replace(hour=00, minute=00, second=00)))).all()
        #print(users)
    return users


async def update_users():
    users_with_folder = await get_users()
    count = 0
    users = []
    folder_counts = {"Нет папки": 0}
    #print(users_with_folder[1])
    users_with_folder_dict = {user[0]: user[1] for user in users_with_folder}
    print(users_with_folder_dict)
    async for dialog in client.get_dialogs(limit=1500):
        messages = [message async for message in client.get_chat_history(dialog.chat.id)]
        if messages[-1].date.date() == date(2024, 10, 25):
            user_id = dialog.chat.id
            users.append(user_id)
            count += 1
            print(count)
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
    print(f'Всего: {count}')




