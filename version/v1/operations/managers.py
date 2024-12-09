import re
from pyrogram.types import Message
from pyrogram import Client
from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.operations.base import BaseOperation
from src.uow.base import BaseUowInterface
from src.utils._utils import get_date_by_weekday


class ManagersOperation(BaseOperation):
    WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    
    def __init__(self, uow: BaseUowInterface, client: Client):
        self.uow: BaseUowInterface = uow()
        self.client = client    
    
    async def __call__(self, message: Message):
        text = message.text
        insert_data = []
        try:
            for weekday in self.WEEKDAYS:
                weekday_shifts = re.search(fr'{weekday}\s*-\s*(.+)', text, re.IGNORECASE)
                if weekday_shifts is None:
                    return await self.client.send_message('me', f"Ошибка! День недели {weekday} не найден")
                weekday_shifts = weekday_shifts.group(1).strip().split()
                date = get_date_by_weekday(weekday).date()
                data = {
                    'date': date,
                    'managers': weekday_shifts
                }
                insert_data.append(data)

            async with self.uow as session:
                await session.shift.insert_bulk(insert_data)
                await session.commit()
                
            await self.client.send_message('me', 'Успешно обновил смены!')
        except Exception as e:
            logger.exception('ERROR')
            await self.client.send_message('me', 'Ошибка! Обратитесь к разработчику')


class AddManagersOperation(BaseOperation):
    
    def __init__(
        self,
        uow: BaseUowInterface,
        client: Client
    ):
        self.uow: BaseUowInterface = uow()
        self.client = client 
    
    async def __call__(self, message: Message):
        async with self.uow as session:
            manager_name = message.command[1]
            try:
                await session.managers.insert_one({'prefix_name': manager_name})
                await session.commit()
            except IntegrityError:
                await message.reply(f"❌ Папка с таким префиксом уже существует")
                return
            
        await message.reply(f"✅ Папка была добавлена в список")