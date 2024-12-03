from pyrogram import filters
from pyrogram.types import Message


async def _manager_name_filter(_, __, message: Message) -> bool:
    """
    Проверяет соответствует ли команда формату:
    - Должно быть ровно 2 части команды
    - Вторая часть должна быть строкой из 2 букв
    """

    if len(message.command) != 2:
        await message.reply('Ошибка: Пожалуйста, укажите две буквы новой папки\nПример: /update_managers Nn')
        return False

    manager_name = message.command[1]

    if len(manager_name) != 2:
        await message.reply(f'Ошибка: в указанном названии папки {manager_name} должно быть только две буквы')
        return False
    
    return True


manager_name = filters.create(_manager_name_filter)