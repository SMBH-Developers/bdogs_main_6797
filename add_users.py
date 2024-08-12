from loguru import logger

from src.config import client
from src.models import db


async def main():
    await client.start()
    async for dialog in client.get_dialogs():
        if not await db.check_user_exists(dialog.chat.id):
            logger.info(f'[{dialog.chat.id}] registered')
            await db.registrate_user(dialog.chat.id)


if __name__ == '__main__':
    try:
        client.run(main())
    finally:
        client.stop()
