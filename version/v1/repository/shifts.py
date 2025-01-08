from typing import Optional, List
from datetime import date
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import selectinload, joinedload, load_only, contains_eager
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .base import BaseRepository
from src.repository.shifts import ShiftRepositoryInterface
from src.database._models import Managers, Shift, ManagersShift
from version.v1.schemas.managers_shifts import ShiftSimple, OutputShift
from loguru import logger


class ShiftsRepository(BaseRepository[Shift, ShiftSimple, OutputShift]):
    '''Является реализацией интерфейса ShiftRepositoryInterface'''
    _model = Shift
    _output_schema = OutputShift
    _input_schema = ShiftSimple


    async def fetch_one(self, date_: date, **filters) -> Optional[OutputShift]:
        stmt = (
            select(self._model)
            .outerjoin(self._model.managers)  # используем LEFT JOIN (outerjoin)
            .options(contains_eager(self._model.managers))  # загружаем связанные данные
            .where(self._model.date == date_)
            .filter_by(**filters)
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
            .outerjoin(self._model.managers)  # LEFT JOIN с таблицей managers
            .options(contains_eager(self._model.managers))  # загружаем связанные данные из JOIN
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
        Добавление или обновление нескольких смен с менеджерами
        Note: Менеджеры должны быть в базе данных, так как мы берем их по префиксу
        '''
        # Получаем всех менеджеров
        all_prefixes = [
            prefix for shift in data for prefix in shift['managers']
        ]
        managers = await self._get_managers_by_prefixes(all_prefixes)
        managers_map = {manager.prefix_name: manager.id for manager in managers}

        # Подготавливаем данные для вставки/обновления
        for shift_data in data:
            # Создаем или обновляем смену
            stmt = pg_insert(self._model).values(date=shift_data['date'])
            stmt = stmt.on_conflict_do_nothing(constraint='shift_date_key')
            await self.session.execute(stmt)

            # Получаем ID смены
            shift_result = await self.session.execute(
                select(self._model.id).where(self._model.date == shift_data['date'])
            )
            shift_id = shift_result.scalar_one()

            # Удаляем старые связи
            await self.session.execute(
                delete(ManagersShift).where(ManagersShift.shift_id == shift_id)
            )

            # Создаем новые связи
            manager_ids = [
                managers_map[m]
                for m in shift_data['managers']
                if m in managers_map
            ]
            if manager_ids:
                await self.session.execute(
                    insert(ManagersShift).values([
                        {"shift_id": shift_id, "manager_id": manager_id}
                        for manager_id in manager_ids
                    ])
                )

    
    async def update_one(self, data: ShiftSimple) -> None:  # TODO: Нужно ли реализовывать?
        ...

    
    async def delete_one(self, id_: int) -> None:  # TODO: Нужно ли реализовывать?
        ...
