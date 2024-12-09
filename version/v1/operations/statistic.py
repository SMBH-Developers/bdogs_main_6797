from datetime import date, datetime

from pyrogram import Client

from src.logic.telegram.folder_managment import AllManagersFactoryInterface
from src.uow.base import BaseUowInterface
from src.operations.base import BaseOperation
from version.v1.schemas.managers_shifts import OutputShift

class StatisticOperation(BaseOperation):
    def __init__(
        self,
        all_managers: AllManagersFactoryInterface,
        uow: BaseUowInterface,
        client: Client
    ):
        self.uow: BaseUowInterface = uow()
        self.client = client
        self.logic = all_managers.stats

    async def __call__(self):
        async with self.uow as session:
            shift: OutputShift = await session.shift.fetch_one(
                date_=date.today(),
                is_deleted=False
            )
            users_without_folder = await session.user.get_count_without_folder()
            await session.commit()
        
        categories_folders_stat = await self.logic.get_folders_statistic(shift=shift)
        stat = '\n\n'.join([category_folders.to_text() for category_folders in categories_folders_stat])
        await self.client.send_message('me', text=stat+f'\n\nПользователей без папки: {users_without_folder}')       
        
        
class StatisticOperationNew(BaseOperation):
    def __init__(
        self,
        all_managers: AllManagersFactoryInterface,
        uow: BaseUowInterface,
        client: Client
    ):
        self.uow: BaseUowInterface = uow()
        self.client = client
        self.logic = all_managers.stats
        
    async def __call__(self):
        async with self.uow as session:
            users_with_folder = await session.user.fetch_all(
                session.user._model.registration_date >= datetime.now().replace(hour=00, minute=00, second=00, microsecond=00)
            )
            await session.commit()
        message = await self.logic.get_folder_stats_today(users_with_folder)
        await self.client.send_message('me', text=message)