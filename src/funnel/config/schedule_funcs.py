from src.constants import FILES_DIR
from src.funnel.types import MyGeneratedMessage
from src.funnel.filters import RegistrationTimeFilter, BotReplyFilter, UserReplyFilter

from .msg_contexts import *

DefaultF = RegistrationTimeFilter


class Config:
    def __init__(self):
        self.diff_days_to_func = {
            '0': self.first_day
        }

    @staticmethod
    async def first_day():
        """Первый день"""
        day_message = [MyGeneratedMessage(DefaultF.create(3), 7, 'text', {'text': FirstDayTexts.msg_1}),
                       MyGeneratedMessage(BotReplyFilter.create(1), 7, 'photo', {'photo': FILES_DIR / 'start.png', 'caption': FirstDayTexts.msg_2}),
                       MyGeneratedMessage(BotReplyFilter.create(1), 7, 'text', {'text': FirstDayTexts.msg_3}, last_message=True)]
        return day_message


class DaysFuncs:
    config: Config = Config()

    async def get_message(self, user_id: int, day: int | str):
        func = self.config.diff_days_to_func[str(day)]
        args = []
        if 'id_' in func.__code__.co_varnames:
            args.append(user_id)
        return await func(*args)
