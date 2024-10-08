from src.funnel.dispatcher_days import Dispatcher
from src.funnel.config.schedule_funcs import DaysFuncs as FunnelConfig


class FunnelsDP:

    @staticmethod
    async def to_funnel(id_: int):
        await Dispatcher().dispatch_funnel_day(id_)
