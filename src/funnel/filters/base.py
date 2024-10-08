__all__ = ["BaseFilter"]


class BaseFilter:

    def __str__(self):
        return f'{type(self).__name__}'

    def __or__(self, other: "BaseFilter"):
        return OrFilter.create(self, other)

    @classmethod
    def create(cls, *args):
        raise NotImplementedError

    async def __call__(self, id_: int, day: str | int, step: str | int, **kwargs) -> bool:
        raise NotImplementedError


class OrFilter(BaseFilter):

    def __init__(self, filter1: BaseFilter, filter2: BaseFilter):
        self._filter1 = filter1
        self._filter2 = filter2

    @classmethod
    def create(cls, filter1: BaseFilter, filter2: BaseFilter):
        return cls(filter1, filter2)

    async def __call__(self, id_: int, day: str | int, step: str | int, **kwargs) -> bool:
        args = (id_, day, step)
        return await self._filter1(*args, **kwargs) or await self._filter2(*args, **kwargs)
