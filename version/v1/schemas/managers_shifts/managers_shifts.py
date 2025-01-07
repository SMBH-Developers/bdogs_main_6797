'''
    Note:
        Если столкнулись с циклическими импортами, то попробуйте использовать этот код:
        Shift.model_rebuild()
        Manager.model_rebuild()
        в конце файла.
        Ошибка была из-за того, что схемы импортировались друг в друга.
'''

from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class BaseSchema(BaseModel):
    """Базовая схема с общей конфигурацией"""
    model_config = ConfigDict(from_attributes=True)


class ShiftBase(BaseSchema):
    """Базовая схема смены"""
    date: date


class ManagerBase(BaseSchema):
    """Базовая схема менеджера"""
    prefix_name: str


class ManagerSimple(ManagerBase):
    pass


class ShiftSimple(ShiftBase):
    managers: Optional[List['ManagerSimple']] = []


class OutputShift(ShiftSimple):
    """Полная схема смены с менеджерами"""
    id: int


class OutputManager(ManagerBase):
    """Полная схема менеджера со сменами"""
    id: int
    # shifts: Optional[List['ShiftSimple']] = []
