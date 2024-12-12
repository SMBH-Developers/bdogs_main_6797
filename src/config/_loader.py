from pyrogram import Client

from src.utils.constants import SESSIONS_DIR
from . import settings, _logger_config


__all__ = ["client"]

if settings.MODE == 'PROD':
    client = Client(str(SESSIONS_DIR / settings.name),
                    settings.api_id, settings.api_hash, phone_number=settings.phone_number
                    )
else:
    client = Client(str(SESSIONS_DIR / 'test'),
                    test_mode=True,
                    in_memory=True
                    )

_logger_config.init()
