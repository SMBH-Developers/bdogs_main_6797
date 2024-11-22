from typing import Optional, List

from sqlalchemy import select, insert, update
from sqlalchemy.orm import selectinload, joinedload

from .base import BaseRepository
from src.database._models import Shift
from version.v1.schemas.managers_shifts import ShiftSimple, OutputShift

class ShiftsRepository(BaseRepository[Shift, ShiftSimple, OutputShift]):
    _model = Shift
    _output_schema = OutputShift
    _input_schema = ShiftSimple

    
    async def fetch_one(self, id_: int, **filters) -> Optional[OutputShift]:
        stmt = (
            select(self._model)
            .options(joinedload(self._model.managers))
            .filter_by(id=id_, **filters)
        )
        result = (await self.session.execute(stmt)).unique().scalar_one_or_none()
        return self._output_schema.model_validate(result) if result else None
    
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
        return [self._output_schema.model_validate(item) for item in result]

    async def insert_one(self, data: ShiftSimple) -> None:
        stmt = insert(self._model).values(**data.model_dump()).returning(self._model)
        result = (await self.session.execute(stmt)).scalar_one()
        return self._output_schema.model_validate(result)
    
    async def insert_bulk(self, data: list[ShiftSimple]) -> None:
        stmt = insert(self._model).values([entity.model_dump() for entity in data])
        await self.session.execute(stmt)

    async def update_one(self, id_: int, data: ShiftSimple) -> None:
        stmt = update(self._model).filter_by(id=id_).values(**data.model_dump())
        await self.session.execute(stmt)

    async def delete_one(self, id_: int) -> None:
        stmt = update(self._model).filter_by(id=id_).values(is_deleted=True)
        await self.session.execute(stmt)