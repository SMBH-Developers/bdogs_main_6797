from datetime import datetime, timedelta

from src.models import db
from src.funnel.types import Timepoint

from .base import BaseFilter


__all__ = ["RegistrationTimeFilter", "UserReplyFilter", "BotReplyFilter"]


class TimepointBaseFilter(BaseFilter):

    timepoint: Timepoint = None

    def __init__(self, time: timedelta):
        if self.timepoint is None:
            raise ValueError("Don't use TimepointBaseFilter")
        self.time = time

    def __str__(self):
        return f'{super().__str__()} with args: {self.time}'

    @classmethod
    def create(cls, minutes: int, hours: int = 0):
        time = timedelta(minutes=minutes, hours=hours)
        return cls(time)

    async def __call__(self, id_: int, day: str | int, step: str | int, **kwargs) -> bool:
        day, step = int(day), int(step)

        if self.timepoint == Timepoint.registration_date:
            day_second = (((day * 24) * 60) * 60)
            timepoint_delta = kwargs.get('funnel_timestamp') or await db.get_funnel_timestamp(id_)
            left_seconds = (datetime.now() - timepoint_delta).total_seconds() - day_second

        elif self.timepoint == Timepoint.bot_reply:
            timepoint_delta = kwargs.get('bot_reply') or await db.get_bot_reply(id_)
            left_seconds = (datetime.now() - timepoint_delta).total_seconds()

        elif self.timepoint == Timepoint.user_reply:
            timepoint_delta = kwargs.get('user_reply') or await db.get_user_reply(id_)
            left_seconds = (datetime.now() - timepoint_delta).total_seconds()

            user_reply_at = timepoint_delta
            bot_reply_at = kwargs.get('bot_reply') or await db.get_bot_reply(id_)
            if bot_reply_at is None or user_reply_at < bot_reply_at:
                return False
        else:
            raise NotImplementedError(f'Unexpected timepoint: {self.timepoint}')

        if self.time.total_seconds() > left_seconds:
            return False
        return True


class RegistrationTimeFilter(TimepointBaseFilter):

    timepoint = Timepoint.registration_date


class UserReplyFilter(TimepointBaseFilter):

    timepoint = Timepoint.user_reply


class BotReplyFilter(TimepointBaseFilter):

    timepoint = Timepoint.bot_reply
