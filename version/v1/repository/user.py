from typing import Optional
from sqlalchemy import select, func
from datetime import datetime
from .base import BaseRepository
from src.repository.user import UserRepositoryInterface
from src.database._models import User
from version.v1.schemas.users import InputUser, OutputUser


class UserRepository(BaseRepository[User, InputUser, OutputUser]):
    '''Является реализацией интерфейса UserRepositoryInterface'''
    _model = User
    _output_schema = OutputUser
    _input_schema = InputUser

    async def fetch_all(self, *filters, offset: int = 0, limit: int = 1000) -> Optional[list[OutputUser]]:
        stmt = select(self._model).filter(*filters).offset(offset).limit(limit)
        result = (await self.session.execute(stmt)).scalars().all()
        if result:
            result = [self._output_schema.model_validate(entity, from_attributes=True) for entity in result]
        return result
    
    async def get_count_without_folder(self) -> int:
        count = (await self.session.execute(
            select(func.count('*')).select_from(User).where(
                User.folder.is_(None),
                User.registration_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )
        )).scalar_one()
        return count
