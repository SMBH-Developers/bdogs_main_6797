from datetime import date
import asyncio

from pyrogram import Client
from sqlalchemy.exc import SQLAlchemyError

from src.logic.telegram.folder_managment import AllManagersFactoryInterface
from src.uow.base import BaseUowInterface
from src.operations.base import BaseOperation
from version.v1.schemas.managers_shifts import OutputShift
from loguru import logger

class DailyFoldersOperation(BaseOperation):
    def __init__(
        self,
        all_managers: AllManagersFactoryInterface,
        uow: BaseUowInterface,
        client: Client
    ):
        self.uow: BaseUowInterface = uow()
        self.client = client
        self.logic = all_managers.daily

    async def __call__(self):
        shift = None
        retraing_count = 3
        while retraing_count > 0:
            try:
                async with self.uow as session:
                    shift: OutputShift = await session.shift.fetch_one(
                        date_=date.today(),
                        is_deleted=False
                    ) # +
                    await session.commit()
                    retraing_count = 0
            except SQLAlchemyError as e:
                logger.error(f'Ошибка при получении смены: {e}')
                await asyncio.sleep(1)
                retraing_count -= 1
        if shift:
            await self.logic.send_users_to_daily_folders(shift=shift, uow=self.uow)
        else:
            logger.error('Смена не найдена')
