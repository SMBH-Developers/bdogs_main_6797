from pathlib import Path
from enum import Enum

BASE_DIR = Path(__file__).parent.parent

ENV_FILE = BASE_DIR / '.env'
DATA_DIR = BASE_DIR / 'data'

FILES_DIR = DATA_DIR / 'files'
SESSIONS_DIR = DATA_DIR / 'sessions'
LOGS_DIR = DATA_DIR / 'logs'

class FolderDay(Enum):
    today = ['Сегодня']
    base = ['База']
    all = ['Сегодня', 'База']
