from typing import Optional, List
from datetime import date
from sqlalchemy import select, insert, update
from sqlalchemy.orm import selectinload, joinedload, load_only

from .base import BaseRepository
from src.repository.shifts import ShiftRepositoryInterface
from src.database._models import Managers, Shift
from version.v1.schemas.managers_shifts import ShiftSimple, OutputShift


class ShiftsRepository(BaseRepository[Shift, ShiftSimple, OutputShift]):
    '''Является реализацией интерфейса ShiftRepositoryInterface'''
    _model = Shift
    _output_schema = OutputShift
    _input_schema = ShiftSimple


    async def fetch_one(self, date_: date, **filters) -> Optional[OutputShift]:
        stmt = (
            select(self._model)
            .options(joinedload(self._model.managers))
            .filter_by(date=date_, **filters)
        )
        result = (await self.session.execute(stmt)).unique().scalar_one_or_none()
        return self._output_schema.model_validate(result, from_attributes=True) if result else None
    
    
    async def fetch_all(
        self, 
        offset: int = 0, 
        limit: int = 1000, 
        **filters
    ) -> List[OutputShift]:
        stmt = (
            select(self._model)
            .options(selectinload(self._model.managers))
            .filter_by(**filters)
            .offset(offset)
            .limit(limit)
        )
        result = (await self.session.execute(stmt)).unique().scalars().all()
        return [self._output_schema.model_validate(item, from_attributes=True) for item in result]

    
    async def _get_managers_by_prefixes(self, prefixes: list[str]) -> list[Managers]:
        stmt = (
            select(Managers)
            .where(Managers.prefix_name.in_(prefixes))
        )
        return (await self.session.execute(stmt)).scalars().all()

    
    async def insert_one(self, data: ShiftSimple) -> None:
        shift = self._model(**data.model_dump(exclude={'managers'}))
        
        if data.managers:
            prefixes = [m.prefix_name for m in data.managers]
            shift.managers = await self._get_managers_by_prefixes(prefixes)
        
        self.session.add(shift)
    
    
    async def insert_bulk(self, data: list[dict]) -> None:
        '''
        Добавление сразу нескольких смен с менеджерами
        Note: Менеджеры должны быть в базе данных, так как мы берем их по префиксу
        '''
        all_prefixes = [
            prefix for shift in data for prefix in shift['managers']
        ]
        managers_map = {
            manager.prefix_name: manager 
            for manager in await self._get_managers_by_prefixes(all_prefixes)
        }
    
        shifts_data = []
        for shift in data:
            shift_obj = self._model(date=shift['date'])
            shift_obj.managers = [
                managers_map[m]
                for m in shift['managers']
                if m in managers_map
            ]
            
            shifts_data.append(shift_obj)
        
        self.session.add_all(shifts_data)

    
    async def update_one(self, data: ShiftSimple) -> None:  # TODO: Нужно ли реализовывать?
        ...

    
    async def delete_one(self, id_: int) -> None:  # TODO: Нужно ли реализовывать?
        ...
