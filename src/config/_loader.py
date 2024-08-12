import json

from pyrogram import Client

from src.constants import SESSIONS_DIR, IGNORE_LIST_PATH
from . import settings, _logger_config


__all__ = ["client"]


client = Client(str(SESSIONS_DIR / settings.name),
                settings.api_id, settings.api_hash, phone_number=settings.phone_number
                )

_logger_config.init()
