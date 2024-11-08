from datetime import datetime, timedelta, time

from pyrogram import types
import aiohttp


__all__ = ["get_date_by_weekday", "extract_card_from_command"]


def get_date_by_weekday(day: str):
    days = {'понедельник': 0, 'вторник': 1, 'среда': 2,
            'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}

    today = datetime.now()
    target_weekday = days[day.lower()]
    if today.weekday() == 6 and today.time() >= time(hour=16):
        days_ahead = target_weekday + 1
    else:
        days_ahead = (target_weekday - today.weekday())

    day_date = today + timedelta(days=days_ahead)
    return day_date


async def extract_card_from_command(message: types.Message) -> str | None:
    if len(message.command) < 2:
        await message.reply('Ошибка: Пожалуйста, укажите номер карты💳.')
        return

    card = message.command[1] if len(message.command) == 2 else ' '.join(message.command[1:])

    if not card.replace(' ', '').isdigit() or 16 < len(card) > 19:
        await message.reply("Ошибка: карта должна содержать только 16 цифр.")
        return

    return card


async def get_name(user_id: int) -> str | bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://212.86.101.9:8854/get_name/{user_id}') as response:
                if response.status == 200:
                    name = (await response.json())
                else:
                    print(f'Ошибка: Не смог получить имя {user_id}')
                    name = False
    except Exception as e:
        print(f'Ошибка API - {e}')
        return False
    return name