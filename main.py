# import asyncio
import re
from datetime import datetime, timedelta

from loguru import logger
from pyrogram import Client, filters, types, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import client
from src.models import db
from src.utils import Additional, get_date_by_weekday


@client.on_message(filters.command('managers') & filters.me)
async def managers(_: Client, message: types.Message):
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    available_managers = set("АЮКЕС")

    managers_shifts = {}
    text = message.text

    try:
        for weekday in weekdays:
            weekday_shifts = re.search(fr'{weekday}\s*-\s*(.+)', text, re.IGNORECASE)
            if weekday_shifts is None:
                return await client.send_message('me', f"Ошибка! День недели {weekday} не найден")
            weekday_shifts = weekday_shifts.group(1)
            if not set(weekday_shifts).issubset(available_managers):
                return await client.send_message('me', f"Ошибка! Доступны только менеджеры: {available_managers}\n"
                                                       f"Указаны {weekday_shifts} за {weekday}"
                                                 )
            managers_shifts[get_date_by_weekday(weekday).date()] = weekday_shifts
        await db.set_managers_shifts(managers_shifts)
        await client.send_message('me', 'Успешно обновил смены!')
    except Exception as e:
        logger.exception('ERROR')
        await client.send_message('me', f'Ошибка! Обратитесь к разработчику\n{e}')


@client.on_message(filters.chat('me') & filters.command('delete_card'))
async def delete_card(_, message: types.Message):
    if len(message.command) < 2:
        await message.reply('Ошибка: Пожалуйста, укажите номер карты💳.')
        return

    card = message.command[1] if len(message.command) == 2 else ' '.join(message.command[1:])
    count = 0

    if not card.replace(' ', '').isdigit() or 16 < len(card) > 19:
        await message.reply("Ошибка: карта должна содержать только 16 цифр.")
        return

    async for search_message in client.search_global(card):
        try:
            if search_message.chat.type.PRIVATE and search_message.text != f'/delete_card {card}':
                await search_message.delete()
                count += 1
        except Exception as e:
            logger.error(f'ERROR DELETE CARD | {e}')

    await client.send_message(message.chat.id, f'✅ Все удалено по карте - {card}. Кол-во сообщений удалено - {count}')


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
