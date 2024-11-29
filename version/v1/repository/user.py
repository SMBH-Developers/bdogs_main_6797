from typing import Optional
from sqlalchemy import select
from .base import BaseRepository
from src.database._models import User
from version.v1.schemas.users import InputUser, OutputUser

class UserRepository(BaseRepository):
    _model = User
    _output_schema = OutputUser
    _input_schema = InputUser

    async def fetch_all(self, offset: int = 0, limit: int = 1000, **filters) -> Optional[list[OutputUser]]:
        stmt = select(self._model).filter(**filters).offset(offset).limit(limit)
        result = (await self.session.execute(stmt)).scalars().all()
        if result:
            result = [self._output_schema.model_validate(entity) for entity in result]
        return result