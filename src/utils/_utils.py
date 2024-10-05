from datetime import datetime, timedelta

from pyrogram import types


__all__ = ["get_date_by_weekday", "extract_card_from_command"]


def get_date_by_weekday(day: str):
    days = {'понедельник': 0, 'вторник': 1, 'среда': 2,
            'четверг': 3, 'пятница': 4, 'суббота': 5, 'воскресенье': 6}

    today = datetime.now()

    target_weekday = days[day.lower()]
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
