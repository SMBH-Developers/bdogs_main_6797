from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from ..config import settings

if settings.MODE == 'TEST':
    DATABASE_PARAMS = {'poolclass': NullPool}
else:
    DATABASE_PARAMS = {}

engine = create_async_engine(settings.postgres_dsn.unicode_string(), **DATABASE_PARAMS)
async_session = async_sessionmaker(engine, expire_on_commit=False)
