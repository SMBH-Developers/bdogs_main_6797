from typing import Awaitable
import asyncio
from datetime import date

from pyrogram import Client
from pyrogram.types import Message
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from src.operations.base import BaseOperation
from src.config.scheduler_singl import SchedulerSingleton
from src.logic.telegram.folder_managment import (
    AllManagersFactoryInterface,
    DialogManagerInterface,
    DailyFoldersManagerInterface,
    )

from src.uow.base import BaseUowInterface


class RegisterUserOperation(BaseOperation):
    def __init__(
        self,
        uow: BaseUowInterface,
        client: Client,
        all_managers: AllManagersFactoryInterface,
        scheduler: SchedulerSingleton,
        ping_function: Awaitable,
        get_name_function: Awaitable,
        ):
        self.uow: BaseUowInterface = uow()
        self.client = client
        self.scheduler = scheduler
        self.ping_function = ping_function
        self.get_name_function = get_name_function
        self.daily_folders_manager: DailyFoldersManagerInterface = all_managers.daily
        self.dialog_manager: DialogManagerInterface = all_managers.dialog
        
    async def _send_text_with_name(self, message: Message, session: BaseUowInterface):
        name = await self.get_name_function(message.from_user.id)
        await asyncio.sleep(10)
        await self.client.send_message(message.from_user.id, text=f'Здравствуйте, {name}! Меня зовут Раяна! ☀️' if name else 'Здравствуйте! Меня зовут Раяна! ☀️')
        await asyncio.sleep(5)
        text = 'Я профессионально занимаюсь диагностикой и чисткой энергетических центров (чакр) и помогаю людям гармонизировать все сферы их жизни с помощью индивидуальных практик уже более 14 лет! 😊\n\nВ своей работе я использую методы энергетической диагностики чакр, а также являюсь экспертом по анализу и коррекции энергетических потоков человека.\n\n📌 Вы можете лучше познакомиться со мной в моем Instagram:\n╚ instagram.com/rayana.soul\n\n🔗 Узнать больше информации обо мне и моих услугах на сайте:\n╚ taplink.cc/rayana_soul\n\n✈️ Подписаться на мой личный telegram-канал:\n╚ @rayana_channel\n\n💬 А так же посмотреть и послушать отзывы о моей работе:\n╚ t.me/+o0R99vpbnw01ZjYy'
        await self.client.send_photo(message.from_user.id, photo='data/files/start.jpg', caption=text)
        self_message = await self.client.send_message(message.from_user.id, text=f'{name + ", п" if name else "П"}одскажите, пожалуйста, Вы ранее проходили диагностику своих чакр?')
        try:
            await session.user.update_one(data={'get_message': True}, id=message.from_user.id)
            await session.commit()
                
            await self.ping_function(
                user_id=message.from_user.id,
                message=self_message,
                scheduler=self.scheduler
            )       
        except SQLAlchemyError as e:
            logger.error(f'[{message.from_user.id}] error update user: {e}')
        
    
    async def __call__(self, message: Message):
        async with self.uow as session:
            user_session = session.user
            if not await user_session.fetch_one(id=message.from_user.id):
                logger.debug(f'User message: [{message.text}], message date: {message.date}')
                await user_session.insert_one(data={'id': message.from_user.id})
                await session.commit()
                logger.info(f'[{message.from_user.id}] user added')
                await self._send_text_with_name(message, session)
                return
            
            elif await user_session.fetch_one(id=message.from_user.id, get_message=True, folder=None):
                shift_today = await session.shift.fetch_one(
                    date_=date.today(),
                    is_deleted=False
                )
                logger.debug(f'shift_today: {shift_today}')
                folders = await self.daily_folders_manager.get_today_folders(shift=shift_today)
                await session.commit()
                managers_today = [manager.prefix_name for manager in shift_today.managers]
                folders = [
                    folder for folder in folders
                    if folder.title.split()[-1] in managers_today
                    and logger.info(f"Папка - {folder.title} Размер - {len(folder.include_peers)}")
                    or True
                ] # хитрость логирования
                
                folder = min(folders, key=lambda folder_x: len(folder_x.include_peers))
                await self.dialog_manager.add_peer_to_filter(folder.title, message.from_user.id)
                await user_session.update_one(data={'folder': folder.title.split()[-1]}, id=message.from_user.id)
                await session.commit()
                return
            
            else:
                logger.debug(f'[{message.from_user.id}] exists')
                return
