from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from ..config import settings
from loguru import logger

# if settings.MODE == 'TEST':
#     DATABASE_PARAMS = {'poolclass': NullPool}
# else:
DATABASE_PARAMS = {
    'pool_pre_ping': True,
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'echo': False,
    'connect_args': {
        # "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
}

engine = create_async_engine(settings.postgres_dsn.unicode_string(), **DATABASE_PARAMS)
async_session = async_sessionmaker(engine, expire_on_commit=False)
