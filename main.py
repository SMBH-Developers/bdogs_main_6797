import asyncio
import aiohttp
import re
from typing import List
from asyncio import Task

from loguru import logger
from pyrogram import Client, filters, types, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from src.config import settings, client
from src.config._settings import developers_ids
from src.models import db
from src.utils import Additional, get_date_by_weekday, extract_card_from_command, get_folder_stats_today, get_name
from src.services import GoogleDP
from src.tasks.scheduler_singl import SchedulerSingleton
from src.tasks.ping.utill import is_last_message_time_read
from src.tasks.ping import ping

from add_users import parse_users

google_dp = GoogleDP()

async def send_text_with_name(message: types.Message, scheduler: SchedulerSingleton):
    name = await get_name(message.from_user.id)
    await asyncio.sleep(80)
    await client.send_message(message.from_user.id, text=f'Здравствуйте, {name}! Меня зовут Раяна! ☀️' if name else 'Здравствуйте! Меня зовут Раяна! ☀️')
    await asyncio.sleep(30)
    text = 'Я профессионально занимаюсь диагностикой и чисткой энергетических центров (чакр) и помогаю людям гармонизировать все сферы их жизни с помощью индивидуальных практик уже более 14 лет! 😊\n\nВ своей работе я использую методы энергетической диагностики чакр, а также являюсь экспертом по анализу и коррекции энергетических потоков человека.\n\n📌 Вы можете лучше познакомиться со мной в моем Instagram:\n╚ instagram.com/rayana.soul\n\n🔗 Узнать больше информации обо мне и моих услугах на сайте:\n╚ taplink.cc/rayana_soul\n\n✈️ Подписаться на мой личный telegram-канал:\n╚ @rayana_channel\n\n💬 А так же посмотреть и послушать отзывы о моей работе:\n╚ t.me/+o0R99vpbnw01ZjYy'
    await client.send_photo(message.from_user.id, photo='data/files/start.jpg', caption=text)
    self_message = await client.send_message(message.from_user.id, text=f'{name + ", Вы" if name else "Вы"} желаете пройти у меня полную диагностику чакр и получить свой персональный разбор, верно?')
    await db.set_send_message(message.from_user.id)
    
    await ping(
       user_id=message.from_user.id,
       message=self_message,
       scheduler=scheduler
    )

# @client.on_message(filters.chat(developers_ids) & filters.command('test-check-message-read-status'))
# async def test_chain_ping(_, message: types.Message):
#     result = await is_last_message_time_read(client, message)
#     await message.reply(f'Result: {result}')

@client.on_message(filters.command('get_statistic') & filters.me)
async def statistic(_: Client, message: types.Message):
    categories_folders_stat = await Additional.get_folders_statistic()
    stat = '\n\n'.join([category_folders.to_text() for category_folders in categories_folders_stat])
    users_without_folder = await db.get_count_without_folder()
    await client.send_message('me', text=stat+f'\n\nПользователей без папки: {users_without_folder}')


@client.on_message(filters.command('get_statistic_new') & filters.me)
async def statistic_new(_: Client, message: types.Message):
    await client.send_message('me', text='Начинаю собирать информацию по папкам сегодня...')
    message = await get_folder_stats_today()
    await client.send_message('me', text=message)


@client.on_message(filters.command('update_managers') & filters.me)
async def add_managers_list(_: Client, message: types.Message):
    if len(message.command) != 2:
        return await message.reply('Ошибка: Пожалуйста, укажите две буквы новой папки\nПример: /update_managers Nn')

    manager_name = message.command[1]

    if len(manager_name) != 2:
        return await message.reply(f'Ошибка: в указанном названии папки {manager_name} должно быть только две буквы')

    await db.update_managers_list(manager_name)
    await message.reply(f"✅ Папка была добавлена в список")


@client.on_message(filters.command('managers') & filters.me)
async def managers(_: Client, message: types.Message):
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    managers_default = await db.get_managers_list()
    available_managers = set(managers_default)

    managers_shifts = {}
    text = message.text

    try:
        for weekday in weekdays:
            weekday_shifts = re.search(fr'{weekday}\s*-\s*(.+)', text, re.IGNORECASE)
            if weekday_shifts is None:
                return await client.send_message('me', f"Ошибка! День недели {weekday} не найден")
            weekday_shifts = weekday_shifts.group(1).strip().split()
            if not set(weekday_shifts).issubset(available_managers):
                return await client.send_message('me', f"Ошибка! Доступны только менеджеры: {available_managers}\n"
                                                       f"Указаны {weekday_shifts} за {weekday}"
                                                 )
            managers_shifts[get_date_by_weekday(weekday).date()] = ' '.join(weekday_shifts)
        await db.set_managers_shifts(managers_shifts)
        await client.send_message('me', 'Успешно обновил смены!')
    except Exception as e:
        logger.exception('ERROR')
        await client.send_message('me', f'Ошибка! Обратитесь к разработчику\n{e}')


@client.on_message(filters.chat('me') & filters.command('black'))
async def black_card(_, message: types.Message):
    card = await extract_card_from_command(message)
    if card is None:
        return

    count = 0
    await db.update_cards_status(int(card.replace(' ', '')), status='black')
    await google_dp.insert_card_google_sheet(int(card.replace(' ', '')), status='black')

    async for search_message in client.search_global(card):
        try:
            if search_message.chat.type.PRIVATE and search_message.text != f'/black {card}' and search_message.text != f'/white {card}':
                await search_message.delete()
                count += 1
        except Exception as e:
            logger.error(f'ERROR DELETE CARD | {e}')

    await client.send_message(message.chat.id, f'✅ Карта добавлена в черный список\nВсе удалено по карте - {card}. Кол-во сообщений удалено - {count}')


@client.on_message(filters.chat('me') & filters.command('white'))
async def white_card(_, message: types.Message):
    card = await extract_card_from_command(message)
    if card is None:
        return

    await db.update_cards_status(int(card.replace(' ', '')), status='white')
    await google_dp.insert_card_google_sheet(int(card.replace(' ', '')), status='white')
    await client.send_message(message.chat.id, f'✅ Карта удалена из черного списка - {card}')


@client.on_message(filters.me & (filters.text | filters.caption))
async def check_our_messages(_, message: types.Message):
    text = message.text if message.text else message.caption
    search_result = re.search(r'\d{16}', text.replace(' ', ''))
    if search_result:
        card = search_result.group()
        if not await db.check_card_status(int(card)):
            await client.send_message('me', f'Ваше сообщение было удалено, т.к карта заблокирована\n\n{message.text}')
            await message.delete()
            logger.info(f'Delete card - {card}')


@client.on_message(filters.private & ~filters.me & ~filters.bot)
async def registration_user(_: Client, message: types.Message):
    logger.debug(f'[{message.from_user.id}] sent message')
    if not await db.check_user_exists(message.from_user.id):
        await db.registrate_user(message.from_user.id)
        scheduler = SchedulerSingleton()
        await asyncio.create_task(send_text_with_name(message, scheduler))
    elif not await db.check_folder(message.from_user.id) and await db.get_message(message.from_user.id):
        folders = await Additional.get_today_folders()
        managers_today = await db.get_managers_today()
        managers_default = ' '.join(await db.get_managers_list())
        folders = [folder for folder in folders if folder.title[-3:].replace(' ', '') in (managers_today if managers_today is not None else managers_default)]
        for folder in folders:
            print(f"Папка - {folder.title} Размер - {len(folder.include_peers)}")
        folder = min(folders, key=lambda folder_x: len(folder_x.include_peers))
        await Additional.add_user_to_folder(folder.title, message.from_user.id)
        await db.set_folder(message.from_user.id, folder.title[-3:].replace(' ', ''))
    else:
        logger.debug(f'[{message.from_user.id}] exists')


async def send_folders_statistic():
    categories_folders_stat = await Additional.get_folders_statistic()
    stat = '\n\n'.join([category_folders.to_text() for category_folders in categories_folders_stat])
    users_without_folder = await db.get_count_without_folder()
    await client.send_message('me', text=stat+f'\n\nПользователей без папки: {users_without_folder}')


async def send_folders_statistic_new():
    message = await get_folder_stats_today()
    await client.send_message('me', text=message)


async def main(scheduler: AsyncIOScheduler):
    await client.start()
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
        coalesce=True
    )
    scheduler.add_job(
        trigger='cron',
        hour='23',
        minute='50',
        func=send_folders_statistic_new,
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True
    )
    scheduler.add_job(
        trigger='cron',
        hour='00',
        minute='00',
        func=Additional.dispatch_users_via_daily_folders,
        replace_existing=True,
        misfire_grace_time=120,
        coalesce=True
    )
    # scheduler.add_job(trigger='cron', minute='*/10', func=google_dp.insert_cards_db)
    scheduler.start()

    await idle()


if __name__ == '__main__':
    scheduler = SchedulerSingleton()
    try:
        client.run(main(scheduler=scheduler))
    finally:
        scheduler.shutdown()
        
