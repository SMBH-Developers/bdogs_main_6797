from pyrogram import Client
from pyrogram import types, raw
from typing import Optional

from .text import PingText

async def is_last_message_time(client: Client, user_id: int, message: types.Message) -> bool:
    '''Проверяет, является ли сообщение последним отправленным'''
    async for msg in client.get_chat_history(user_id, limit=1):
        if msg.outgoing and msg.date == message.date:
            return True
    return False

async def is_last_message_time_read(client: Client, message: types.Message) -> Optional[bool]:
    return await check_message_read_status(client, message)

async def check_message_read_status(client: Client, message: types.Message) -> Optional[bool]:
    '''Peers - это чаты или каналы'''
    peer: raw.base.InputPeer  = await client.resolve_peer(message.chat.id)
    dialogs: list[raw.types.Dialog] = await client.invoke(
        raw.functions.messages.GetPeerDialogs(
            peers=[
                raw.types.InputDialogPeer(peer) # возможно просто peer передать
            ]
        ),
        retries=3,
        sleep_threshold=30
    )

    for dialog in dialogs:
        if message.id < dialog.read_outbox_max_id: # если сообщение прочитано
            return True


async def send_ping(client: Client, user_id: int, ping_step: str, name: Optional[str] = None):
    text = PingText[ping_step].value.format(name=name)
    await client.send_message(user_id, text)
