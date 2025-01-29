from pyrogram import Client, filters, types, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from src.config import client
from src.config.scheduler_singl import SchedulerSingleton
from src.filtres import manager_name
from bootstrap import bootstrap_
from version.v1.tasks.daily import (
    send_folders_statistic,
    send_folders_statistic_new,
    dispatch_users_via_daily_folders
)
from loguru import logger
from src.utils.constants import ADMIN_IDS

@client.on_message(filters.chat(ADMIN_IDS) & ~filters.me & ~filters.bot & filters.command('insert_users'))
async def insert_users(_: Client, message: types.Message):
    logger.info(f'Зашел')
    async for dialog in client.get_dialogs():
        async for message in client.get_chat_history(dialog.chat.id):
            if message.date.date() < datetime.now().replace(month=1, day=12).date():
                break

            if message.from_user is None:
                logger.warning(f'Пропустил сообщение без отправителя: {message}')
                continue

            try:
                await bootstrap_["register_user"](message)
            except Exception as e:
                logger.error(f'Ошибка при добавлении пользователя: {e}')


@client.on_message(filters.command('get_statistic') & filters.me)
async def statistic(_: Client, message: types.Message): # TODO: Узнать зачем этот обработчик
    await bootstrap_["statistic"]()


@client.on_message(filters.command('get_statistic_new') & filters.me)
async def statistic_new(_: Client, message: types.Message):
    await client.send_message('me', text='Начинаю собирать информацию по папкам сегодня...')
    await bootstrap_["statistic_new"]()


@client.on_message(filters.command('update_managers') & filters.me) # "& manager_name" (проверяет два ли символа после команды)
async def add_managers_list(_: Client, message: types.Message):
    await bootstrap_["add_managers"](message)


@client.on_message(filters.command('managers') & filters.me)
async def managers(_: Client, message: types.Message):
    await bootstrap_["managers"](message)


@client.on_message(filters.chat('me') & filters.command('black'))
async def black_card(_, message: types.Message):
    count = await bootstrap_["black_card"](message)
    await client.send_message(
        message.chat.id,
        f'✅ Карта добавлена в черный список\n Кол-во сообщений удалено - {count}'
        if count is not None else '❌ Ошибка при добавлении карты в черный список'
        )


@client.on_message(filters.chat('me') & filters.command('white'))
async def white_card(_, message: types.Message):
    is_success = await bootstrap_["white_card"](message)
    await client.send_message(
        message.chat.id,
        f'✅ Карта удалена из черного списка' if is_success else '❌ Ошибка при удалении карты из черного списка'
    )


@client.on_message(filters.me & (filters.text | filters.caption))
async def moderate_card_numbers(_, message: types.Message):
    await bootstrap_["moderate_card_numbers"](message)


@client.on_message(filters.private & ~filters.me & ~filters.bot)
async def registration_user(_: Client, message: types.Message):
    await bootstrap_["register_user"](message)


async def main(scheduler: AsyncIOScheduler):
    await client.start()
    logger.info('Client started')
    # managers_today = await db.get_managers_today()
    # print(managers_today.split(" ") if managers_today is not None else ['Су', 'Ек2', 'Ка', 'Ек', 'Ан', 'Эл', 'Та', 'Ве'])
    # asyncio.create_task(parse_users())
    scheduler.add_job(
        trigger='cron',
        hour='23',
        minute='56',
        func=send_folders_statistic,
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True,
        id='send_folders_statistic'
    )
    scheduler.add_job(
        trigger='cron',
        hour='23',
        minute='50',
        func=send_folders_statistic_new,
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True,
        id='send_folders_statistic_new'
    )
    scheduler.add_job(
        trigger='cron',
        hour='11', # 00
        minute='43', # 00
        func=dispatch_users_via_daily_folders,
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True,
        id='dispatch_users_via_daily_folders'
    )
    # scheduler.add_job(trigger='cron', minute='*/10', func=google_dp.insert_cards_db)
    scheduler.start()

    await idle()


if __name__ == '__main__':
    scheduler = SchedulerSingleton()
    try:
        client.run(main(scheduler))
    finally:
        client.stop()
        scheduler.shutdown()
