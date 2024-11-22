from pyrogram.raw.types import DialogFilter
from pyrogram.raw.base import InputPeer

class FolderUtils:
    @staticmethod
    async def users_to_peers(users_ids: list[int] | set[int], *, ignore_peer_invalid: bool = False):
        ...
    
    @staticmethod
    def group_folders(folders: list[DialogFilter]) -> dict[str, list[DialogFilter]]:
        ...
    
    @classmethod
    def extract_ids_from_peers(cls, peers: list[InputPeer]) -> set[int]:
        ...

    