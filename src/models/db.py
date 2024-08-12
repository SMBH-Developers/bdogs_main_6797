from sqlalchemy import select

from src.models._engine import async_session
from ._models import *


async def registrate_user(id_: int):
    async with async_session() as session:
        user = User(id=id_)
        session.add(user)
        await session.commit()


async def check_user_exists(id_: int) -> bool:
    async with async_session() as session:
        exists = (await session.execute(select(User.id).where(User.id == id_).limit(1))).one_or_none()
    if exists is None:
        return False
    return True
