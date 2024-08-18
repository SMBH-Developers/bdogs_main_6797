# import asyncio
import re
from datetime import datetime, timedelta

from loguru import logger
from pyrogram import Client, filters, types, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import client
from src.models import db
from src.utils import Additional


def get_date_by_weekday(day: str):
    days = {'понедельник': 0, 'вторник': 1, 'среда': 2,
            'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}

    today = datetime.now()

    target_weekday = days[day.lower()]
    days_ahead = (target_weekday - today.weekday()) % 7

    day_date = today + timedelta(days=days_ahead)
    return day_date


@client.on_message(filters.command('managers') & filters.me)
async def managers(_: Client, message: types.Message):
    if len(message.command) < 1:
        await client.send_message('me', 'Вы не передали параметры для команды')
        return

    managers_dict = {}
    param = " ".join(message.command[1:])
    parts = re.findall(r'(\w+)\s*—\s*(\w+)', param)

    try:
        for day, value in parts:
            managers_dict[get_date_by_weekday(day).strftime("%Y-%m-%d")] = value
    #     for param in message.command[1:]:
    #         parts = re.findall(r'', param)
    #         # parts = param.split('—')
    #         if len(parts) == 2:
    #             day = parts[0].strip().lower()
    #             value = parts[1].strip()
    #             managers_dict[get_date_by_weekday(day).strftime("%Y-%m-%d")] = value
        await db.set_managers_shifts(managers_dict)
        await client.send_message('me', 'Успешно обновил смены!')
    except Exception as e:
        await client.send_message('me', f'Ошибка! Обратитесь к руководству\n{e}')


@client.on_message(group=2)
async def got_message(_: Client, message: types.Message):
    if hasattr(message, 'from_user'):
        logger.debug(f'Second handler got message by [{message.from_user.id}]')


@client.on_message(filters.private & ~filters.me & ~filters.bot)
async def registration_user(_: Client, message: types.Message):
    logger.debug(f'[{message.from_user.id}] sent message')
    if not await db.check_user_exists(message.from_user.id):
        await db.registrate_user(message.from_user.id)
        folders = await Additional.get_today_folders()
        folder = min(folders, key=lambda folder_x: len(folder_x.include_peers))
        await Additional.add_user_to_folder(folder.title, message.from_user.id)
    else:
        logger.debug(f'[{message.from_user.id}] exists')


async def send_folders_statistic():
    categories_folders_stat = await Additional.get_folders_statistic()
    stat = '\n\n'.join([category_folders.to_text() for category_folders in categories_folders_stat])
    await client.send_message('me', text=stat)


async def main():
    await client.start()

    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(trigger='cron', hour='23', minute='59', func=send_folders_statistic)
    scheduler.add_job(trigger='cron', hour='0', minute='0', func=Additional.dispatch_users_via_daily_folders)
    scheduler.start()

    await idle()


def on_shutdown():
    client.stop()


if __name__ == '__main__':
    # logging.basicConfig()
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    try:
        client.run(main())
    finally:
        on_shutdown()
