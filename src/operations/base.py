from abc import ABC, abstractmethod
from src.logic.google.google_sheet import GoogleSheetInterface
from src.uow.base import BaseUowInterface
from pyrogram import Client
from pyrogram.types import Message

from src.utils import extract_card_from_command

class BaseOperation(ABC):
    ...
    
    
