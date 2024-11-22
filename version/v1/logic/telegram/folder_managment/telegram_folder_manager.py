class TelegramFolderManager:
    @staticmethod
    async def get_new_folder_id() -> int:
        ...
    
    @classmethod
    async def add_user_to_folder(cls, folder_title: str, user_id: int):
        ...
