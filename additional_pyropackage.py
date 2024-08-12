from typing import Callable, Optional, Tuple, List
import asyncio
import pyrogram
from pyrogram import Client
from pyrogram import raw

client = Client(name="Main_7491", api_id=28153256, api_hash="b0dd35218d3a51ee833eefbafad508ff",
                phone_number="+88803467491")


class Additional:
    @staticmethod
    async def get_new_folder_id(p_client: pyrogram.Client) -> int:
        folders = list(filter(
            lambda x: hasattr(x, 'id'),
            await p_client.invoke(raw.functions.messages.GetDialogFilters()))
        )
        return max(folders, key=lambda x: x.id).id + 1 if folders else 10

    @staticmethod
    async def get_dialog_filters(
            p_client: pyrogram.Client,
            folders_filter: Optional[Callable] = None
    ) -> List[raw.types.DialogFilter | raw.types.DialogFilterDefault]:

        folders = await p_client.invoke(raw.functions.messages.GetDialogFilters())
        updated_folders = [folder for folder in folders if not folders_filter or folders_filter(folder)]
        return updated_folders

    @classmethod
    async def add_user_to_folder(
            cls,
            p_client: pyrogram.Client,
            users_id: list[int],
            folder_id: int = None,
            folder_title: str = None
            ) -> bool:
        folder_filters = await cls.get_dialog_filters(
            p_client,
            lambda folder: (hasattr(folder, 'id') and folder.id == folder_id) or
                           (hasattr(folder, 'title') and folder.title.lower() == folder_title)
            )

        if folder_filters:
            folder_filters = folder_filters[0]
            folder_id = folder_filters.id
        else:
            # create new folder if not found folder with id/title
            folder_id = await cls.get_new_folder_id(p_client)
            folder_filters = pyrogram.raw.types.DialogFilter(
                id=folder_id,
                title=folder_title or 'manual',
                pinned_peers=raw.core.List([]),
                include_peers=raw.core.List([]),
                exclude_peers=raw.core.List([]),
                contacts=False, non_contacts=False, groups=False, broadcasts=False,
                bots=False, exclude_muted=False, exclude_read=False, exclude_archived=True,
                emoticon=''
            )
        users_for_folder = []
        for user_id in users_id:
            new_peer = await p_client.resolve_peer(user_id)
            users_for_folder.append(new_peer)
        folder_filters.include_peers = raw.core.List(users_for_folder)
        return await p_client.invoke(raw.functions.messages.UpdateDialogFilter(id=folder_id, filter=folder_filters))

    @classmethod
    async def get_all_users_folder(cls, p_client: pyrogram.Client):
        folder_filters = await cls.get_dialog_filters(p_client)

        users_id = []
        folders_title = ['А', 'Ю', 'К', 'Е']
        folder_day = ['Послезавтра ', 'Завтра ', 'Сегодня ']

        for folder_filter in folder_filters:
            for user in folder_filter.include_peers:
                for i, day in enumerate(folder_day):
                    if folder_filter.title.startswith(day) and not folder_filter.title.startswith('Послезавтра'):
                        folder_name = folder_day[i + 1] + folders_title[i % len(folders_title)]
                        users_id.append(user.user_id)
                    elif folder_filter.title.startswith('Послезавтра'):
                        pass

        for day in folder_day:
            await cls.add_user_to_folder(p_client, users_id=users_id, folder_title=day)  #TODO


async def main():
    async with client:
        print(await Additional.get_dialog_filters(client))


if __name__ == '__main__':
    # pass
    # Другой прайс folder_id = 2
    asyncio.run(main())
