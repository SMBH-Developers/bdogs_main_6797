from pydantic import BaseModel, field_validator
from typing import Optional, Union

CardType = Union[int, str]
StatusType = str


class InputCardSheet(BaseModel):
    cards: Optional[dict[CardType, StatusType]]
    
    @field_validator('cards')
    def validate_card(cls, v: Optional[dict]) -> dict:
        if v is None:
            return {}
        return {(int(k) if isinstance(k, str) else k): val for k, val in v.items()}

class InputCard(BaseModel):
    card: CardType
    status: StatusType
    
    @field_validator('card')
    def validate_card(cls, v: CardType) -> CardType:
        return int(v) if isinstance(v, str) else v

class OutputCard(InputCard):
    id: int
