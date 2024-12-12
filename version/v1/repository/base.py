from loguru import logger
from sqlalchemy import insert, select, update, delete
from typing import Optional, Type, Union
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.repository.base import BaseRepositoryInterface, Model, InputSchema, OutputSchema


class BaseRepository(BaseRepositoryInterface[Model, InputSchema, OutputSchema]):
    _model: Type[Model]
    _output_schema: Type[OutputSchema]
    _input_schema: Type[InputSchema]
    
    
    async def fetch_one(self, **filters) -> Optional[OutputSchema]:
        stmt = select(self._model).filter_by(**filters)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result:
            result = self._output_schema.model_validate(result, from_attributes=True)
        return result

    async def fetch_all(
        self, 
        offset: int = 0, 
        limit: int = 1000, 
        **filters
    ) -> Optional[list[OutputSchema]]:
        stmt = select(self._model).filter_by(**filters).offset(offset).limit(limit)
        result = (await self.session.execute(stmt)).scalars().all()
        if result:
            result = [self._output_schema.model_validate(entity, from_attributes=True) for entity in result]
        return result

    async def insert_one(self, data: Union[InputSchema, dict]) -> None:
        values = data.model_dump() if isinstance(data, InputSchema) else data
        stmt = insert(self._model).values(**values).returning(self._model)
        result = (await self.session.execute(stmt)).scalar_one()
        return self._output_schema.model_validate(result, from_attributes=True)
    
    async def insert_bulk(self, data: list[Union[InputSchema, dict]]) -> None:
        values = [entity.model_dump() for entity in data] if isinstance(data[0], InputSchema) else data
        stmt = insert(self._model).values(values)
        await self.session.execute(stmt)

    async def update_one(self, *, data: Union[InputSchema, dict], **filters) -> None:
        values = data.model_dump() if isinstance(data, InputSchema) else data
        stmt = update(self._model).filter_by(**filters).values(**values)
        await self.session.execute(stmt)

    async def delete_one(self, *, strong: bool = False, **filters) -> None:
        if not strong:
            stmt = update(self._model).filter_by(**filters).values(is_deleted=True)
        else:
            stmt = delete(self._model).filter_by(**filters)
        await self.session.execute(stmt)
