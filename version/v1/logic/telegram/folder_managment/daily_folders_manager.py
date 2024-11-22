from pyrogram.raw.types import DialogFilter
from pyrogram import raw, errors
from src.logic.telegram.folder_managment import DailyFoldersManagerInterface, DialogManagerInterface, FolderUtilsInterface
from loguru import logger
from pyrogram import Client

from src.uow.base import BaseUowInterface

class DailyFoldersManager(DailyFoldersManagerInterface):
    
    def __init__(
        self,
        client: Client,
        uow: BaseUowInterface,
        dialog_manager: DialogManagerInterface,
        folder_utils: FolderUtilsInterface
    ):
        self.client = client
        self.uow = uow
        self.dialog_manager = dialog_manager
        self.folder_utils = folder_utils
    
    async def _get_daily_folders_titles(self) -> set[str]:
        '''
        Example:
            {'Сегодня Ан', 'Сегодня Ве', 'Сегодня Ка', 'Сегодня Ек', 'Сегодня Ек2', 'Сегодня Эл', 'Сегодня Та', 'База Ан', 'База Ве', 'База Ка', 'База Ек', 'База Ек2', 'База Эл', 'База Та'}
        '''
        async with self.uow as session:
            managers = await db.get_managers_today()
            managers_default = await db.get_managers_list()
            folders_categories = managers.split(" ") if managers else managers_default
            folders_days = ['Сегодня', 'База']
            folders_titles = {f'{folder_day} {folder_category}' for folder_day in folders_days
                          for folder_category in folders_categories
                          }
        return folders_titles
    
    async def get_daily_folders(self) -> list[DialogFilter]:
        folders_titles = await self._get_daily_folders_titles()

        # Getting necessary folders
        folders_filters = [lambda folder: hasattr(folder, 'title') and folder.title in folders_titles]
        folders = await self.dialog_manager.get_dialog_filters(lambda folder: any([filter_(folder) for filter_ in folders_filters]))
        return folders
    
    async def get_today_folders(self) -> list[DialogFilter]:
        managers_today: list[] = await db.get_managers_today()
        titles = [f'Сегодня {category}' for category in managers]
        folders = await self.dialog_manager.get_dialog_filters(lambda folder: hasattr(folder, 'title') and folder.title in titles)
        return folders
    
    
    async def send_users_to_daily_folders(self):
        with logger.catch():
            logger.info('Function **dispatch_users_via_daily_folders** started')
            # Getting necessary folders
            folders = await self.get_daily_folders()
            logger.info(f'FOLDERS | get_daily_folders  -  {folders}')
            folders_titles = set(folder.title for folder in folders)
            logger.info(f'FOLDERS | folders title  -  {folders}')

            # Creating non existing folders
            non_existing_folders_titles = await self._get_daily_folders_titles() - folders_titles
            logger.info(f'FOLDERS | non existing folders titles  -  {folders}')
            folders.extend([await self.dialog_manager.create_dialog_filter(title) for title in non_existing_folders_titles])

            grouped_folders = self.folder_utils.group_folders(folders)
            for category, category_folders in grouped_folders.items():
                # print(f'Папка - {category}\nСодержимое - {category_folders}')
                total_folder, today_folder = category_folders
                # print(f'База - {total_folder}\n\nСегодня - {today_folder}\n\n')

                today_folder: DialogFilter
                total_folder: DialogFilter
                general_set_today = today_folder.pinned_peers + today_folder.include_peers
                general_set_total = total_folder.pinned_peers + total_folder.include_peers

                free_places_total_count = 200 - len(general_set_total)
                logger.info(f'FOLDERS | Free places total count - {free_places_total_count}')
                if len(general_set_today) > free_places_total_count:
                    users_to_del_count = len(general_set_today) - free_places_total_count
                else:
                    users_to_del_count = 0
                logger.info(f'FOLDERS | Count users to delete - {users_to_del_count}')

                old_users_to_delete = await db.get_old_users(users_to_del_count, self.folder_utils.extract_ids_from_peers(general_set_total))

                logger.info(f'FOLDERS | Start exctract ids from peers')
                users = (
                    self.folder_utils.extract_ids_from_peers(general_set_total) |
                    self.folder_utils.extract_ids_from_peers(general_set_today)
                ) - set(old_users_to_delete)
                logger.info(f'FOLDERS | End exctract ids from peers')
                total_folder.include_peers = raw.core.List(await self.folder_utils.users_to_peers(users, ignore_peer_invalid=True))

                # **** Dont touch next
                # In the end we clear Today directory
                today_folder.include_peers = raw.core.List([await self.client.resolve_peer('me')])
                today_folder.pinned_peers = raw.core.List([])
                logger.info(f'FOLDERS | Clear Today folder')
                # Update today and total folders:
                logger.info(f'FOLDERS | Start insert users in folders - Today and Total')
                await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=today_folder.id, filter=today_folder))
                logger.info(f'FOLDERS | Inserted users in folder Today')
                await self.client.invoke(raw.functions.messages.UpdateDialogFilter(id=total_folder.id, filter=total_folder))
                logger.info(f'FOLDERS | Inserted users in folder Total')

