from loguru import logger
from pyrogram.raw.types import DialogFilter
from pyrogram import raw, errors
from src.logic.telegram.tasks_mexin.daily_folders import DailyFoldersMexinInterface
import asyncio
from src.uow.base import BaseUowInterface

class DailyFoldersMexin(DailyFoldersMexinInterface):
    async def send_users_to_daily_folders(self, shift: 'OutputShift', uow: BaseUowInterface):
        with logger.catch():
            logger.info('Function **dispatch_users_via_daily_folders** started')
            # Getting necessary folders
            folders = await self.get_daily_folders(shift=shift)
            # logger.info(f'FOLDERS | get_daily_folders  -  {folders}')
            folders_titles = set(folder.title for folder in folders)
            # logger.info(f'FOLDERS | folders title  -  {folders}')

            # Creating non existing folders
            non_existing_folders_titles = await self._get_daily_folders_titles(shift=shift) - folders_titles
            logger.info(f'FOLDERS | non existing folders titles  -  {non_existing_folders_titles}')
            logger.debug(f'FOLDERS | folders titles  -  {folders_titles}')
            
            # new_folders = []
            # for title in non_existing_folders_titles:
            #     new_folder = await self.dialog_manager.create_dialog_filter(
            #         new_folder_id=await self.folder_utils.get_new_folder_id(),
            #         title=title,
            #         users=await self.folder_utils.get_default_users()
            #     )
            #     new_folders.append(new_folder)
            #     await asyncio.sleep(0.5)  # Задержка 500ms между запросами
            
            # folders.extend(new_folders)

            grouped_folders = self.folder_utils.group_folders(folders)
            for category, category_folders in grouped_folders.items():
                logger.debug(f'FOLDERS | Processing category  -  {category}')
                total_folder, today_folder = category_folders
                
                today_folder: DialogFilter
                total_folder: DialogFilter
                general_set_today = today_folder.pinned_peers + today_folder.include_peers
                general_set_total = total_folder.pinned_peers + total_folder.include_peers
                
                logger.debug(f'FOLDERS | {category} | Before processing:')
                logger.debug(f'FOLDERS | {category} | Today folder ({today_folder.title}): {len(general_set_today)} users')
                logger.debug(f'FOLDERS | {category} | Total folder ({total_folder.title}): {len(general_set_total)} users')
                
                # Логируем расчет количества пользователей для удаления
                free_places_total_count = 200 - len(general_set_total)
                logger.debug(f'FOLDERS | {category} | Free places in total folder: {free_places_total_count}')
                if len(general_set_today) > free_places_total_count:
                    users_to_del_count = len(general_set_today) - free_places_total_count
                else:
                    users_to_del_count = 0
                logger.debug(f'FOLDERS | {category} | Users to delete: {users_to_del_count}')
                
                # Логируем извлечение пользователей
                old_users_ids = self.folder_utils.extract_ids_from_peers(general_set_total)
                logger.debug(f'FOLDERS | {category} | Old users IDs: {old_users_ids}')
                
                # Логируем перед асинхронной операцией
                async with uow as session:
                    old_users_to_delete = await session.user.fetch_all(
                        session.user._model.id.in_(old_users_ids),
                        limit=users_to_del_count,
                    )
                    logger.debug(f'FOLDERS | {category} | Old users to delete: {[user.id for user in old_users_to_delete]}')
                    await session.commit()
                
                # Логируем после обработки
                logger.debug(f'FOLDERS | {category} | After processing:')
                logger.debug(f'FOLDERS | {category} | Today folder ({today_folder.title}): {len(today_folder.include_peers)} users')
                logger.debug(f'FOLDERS | {category} | Total folder ({total_folder.title}): {len(total_folder.include_peers)} users')

                logger.info(f'FOLDERS | Start exctract ids from peers')
                # users = (
                #     self.folder_utils.extract_ids_from_peers(general_set_total) |
                #     self.folder_utils.extract_ids_from_peers(general_set_today)
                # ) - {user.id for user in old_users_to_delete}
                # logger.info(f'FOLDERS | End exctract ids from peers')
                # total_folder.include_peers = raw.core.List(await self.folder_utils.users_to_peers(users, ignore_peer_invalid=True))

                # **** Dont touch next
                # In the end we clear Today directory
                # today_folder.include_peers = raw.core.List([await self.client.resolve_peer('me')])
                # today_folder.pinned_peers = raw.core.List([])
                # logger.info(f'FOLDERS | Clear Today folder')
                # # Update today and total folders:
                # logger.info(f'FOLDERS | Start insert users in folders - Today and Total')
                # await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=today_folder.id, filter=today_folder))
                # logger.info(f'FOLDERS | Inserted users in folder Today')
                # await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=total_folder.id, filter=total_folder))
                # logger.info(f'FOLDERS | Inserted users in folder Total')

