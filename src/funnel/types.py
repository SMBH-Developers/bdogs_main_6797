from enum import Enum
from dataclasses import dataclass
from datetime import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .filters.base import BaseFilter


class Timepoint(Enum):
    registration_date = "registration_date"
    user_reply = "user_reply"
    bot_reply = "bot_reply"


@dataclass
class MyGeneratedMessage:
    filter: "BaseFilter"
    seconds_wait_before_sending: int
    content_type_to_send: str
    others_kwargs: dict
    trigger_from_our_account_to_cancel: list | None = None
    trigger_from_user_account_to_send: list | None = None
    last_message: bool = False
    time_send: time | None = None  # TODO: Filter

    def __post_init__(self):
        self.filter.message = self
