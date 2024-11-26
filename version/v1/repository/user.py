from .base import BaseRepository
from src.database._models import User
from version.v1.schemas.users import InputUser, OutputUser

class UserRepository(BaseRepository):
    _model = User
    _output_schema = OutputUser
    _input_schema = InputUser
