from loguru import logger
from sqlalchemy import insert, select, update
from typing import Optional, Type

from src.repository.base import BaseRepositoryInterface, Model, InputSchema, OutputSchema

class BaseRepository(BaseRepositoryInterface[Model, InputSchema, OutputSchema]):
    _model: Type[Model]
    _output_schema: Type[OutputSchema]
    _input_schema: Type[InputSchema]
    
    async def fetch_one(self, id_: int, **filters) -> Optional[OutputSchema]:
        stmt = select(self._model).filter_by(id=id_, **filters)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result:
            result = self._output_schema.model_validate(result)
        return result
    
    async def fetch_all(self, offset: int = 0, limit: int = 1000, **filters) -> Optional[list[OutputSchema]]:
        stmt = select(self._model).offset(offset).limit(limit).filter_by(**filters)
        result = (await self.session.execute(stmt)).scalars().all()
        if result:
            result = [self._output_schema.model_validate(entity) for entity in result]
        return result

    async def insert_one(self, data: InputSchema) -> None:
        stmt = insert(self._model).values(**data.model_dump()).returning(self._model)
        result = (await self.session.execute(stmt)).scalar_one()
        return self._output_schema.model_validate(result)
    
    async def insert_bulk(self, data: list[InputSchema]) -> None:
        stmt = insert(self._model).values([entity.model_dump() for entity in data])
        await self.session.execute(stmt)

    async def update_one(self, id_: int, data: InputSchema) -> None:
        stmt = update(self._model).filter_by(id=id_).values(**data.model_dump())
        await self.session.execute(stmt)

    async def delete_one(self, id_: int) -> None:
        stmt = update(self._model).filter_by(id=id_).values(is_deleted=True)
        await self.session.execute(stmt)
