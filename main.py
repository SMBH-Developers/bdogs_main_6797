import asyncio

from pyrogram import Client, filters, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import client
from src.models import db
from src.utils import Additional


@client.on_message(filters.private & ~filters.me & ~filters.bot)
async def registration_user(_: Client, message: types.Message):
    if not await db.check_user_exists(message.from_user.id):
        await db.registrate_user(message.from_user.id)
        folders = await Additional.get_today_folders()
        folder = min(folders, key=lambda folder_x: len(folder_x.include_peers))
        await Additional.add_user_to_folder(folder.title, message.from_user.id)


async def send_folders_statistic():
    folders_stat = await Additional.get_folders_statistic()
    await client.send_message('me', text='\n'.join([f'{folder_stat.folder_title} - {folder_stat.peers_len}' for folder_stat in folders_stat]))


def main():
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(trigger='cron', hour='23', minute='55', func=send_folders_statistic)
    scheduler.add_job(trigger='cron', hour='23', minute='59', func=Additional.dispatch_users_via_daily_folders)
    scheduler.start()



try:
    client.run(main())
finally:
    pass
