from typing import Optional
import asyncio

from pyrogram import Client
from pyrogram import types, raw
from loguru import logger

from .text import PingText


async def is_last_message_time(client: Client, user_id: int, message: types.Message) -> bool:
    '''Проверяет, является ли сообщение последним отправленным'''
    try:
        async for msg in client.get_chat_history(user_id, limit=1):
            if msg.outgoing and msg.date == message.date:
                return True
    except BaseException as e:
        logger.error(f'Error checking last message time for user {user_id}: {e}')
        
    return False


async def is_last_message_time_read(client: Client, message: types.Message) -> Optional[bool]:
    try:
        return await check_message_read_status(client, message)
    except BaseException as e:
        logger.error(f'Error checking last message read status for user {message.chat.id}: {e}')
        
    return False


async def check_message_read_status(client: Client, message: types.Message) -> Optional[bool]:
    '''Peers - это чаты или каналы'''
    peer: raw.base.InputPeer  = await client.resolve_peer(message.chat.id)
    dialogs: list[raw.types.Dialog] = await client.invoke(
        raw.functions.messages.GetPeerDialogs(
            peers=[
                raw.types.InputDialogPeer(peer=peer) # возможно просто peer передать
            ]
        ),
        retries=3,
        sleep_threshold=30
    )

    for dialog in dialogs.dialogs:
        if message.id <= dialog.read_outbox_max_id: # если сообщение прочитано
            return True


async def send_ping(
    client: Client,
    user_id: int,
    ping_step: str,
    name: Optional[str] = None
) -> Optional[types.Message]:
    try:
        text = PingText.paginate(ping_step, name)
        message: types.Message = await client.send_message(user_id, text)
        await asyncio.sleep(1)
        logger.info(f'Send ping for user {user_id} with ping step {ping_step}')
        return message
    
    except BaseException as e:
        logger.error(f'Error sending ping for user {user_id}: {e}')
    return
