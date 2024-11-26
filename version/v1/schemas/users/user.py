from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class InputUser(BaseModel):
    folder: Optional[str]


class OutputUser(InputUser):
    id: int
    registration_date: datetime
    get_message: bool
    ping_step: Optional[str]
