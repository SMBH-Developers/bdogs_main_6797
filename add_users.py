import asyncio

from src.config import client
from src.models import db


async def check_dialogs():
    await client.start()
    async for dialog in client.get_dialogs():
        if not await db.check_user_exists(dialog.chat.id):
            await db.registrate_user(dialog.chat.id)


if __name__ == '__main__':
    try:
        asyncio.run(client.run())
    finally:
        client.stop()
