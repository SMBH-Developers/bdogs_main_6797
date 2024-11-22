from .base import BaseRepository
from src.database._models import Managers
from version.v1.schemas.managers_shifts import ManagerSimple, OutputManager


class ManagersRepository(BaseRepository[Managers, ManagerSimple, OutputManager]):
    _model = Managers
    _output_schema = OutputManager
    _input_schema = ManagerSimple
