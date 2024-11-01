from loguru import logger

from src.config import client
from src.models import db


async def parse_users():
    async for dialog in client.get_dialogs():
        count_messages = 0
        async for message in client.get_chat_history(dialog.chat.id):
            count_messages += 1
        logger.info(f'User - [{dialog.chat.id}] have {count_messages} messages')
    logger.info('End parse users')
        #if not await db.check_user_exists(dialog.chat.id):
        #    logger.info(f'[{dialog.chat.id}] registered')
        #    await db.registrate_user(dialog.chat.id)
