from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from src.schemas.books import BookRead


class ExchangeOfferRole(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"


class ExchangeOfferCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    offered_book_id: int
    requested_book_id: int


class ExchangeOfferRead(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    offered_book_id: int
    requested_book_id: int
    offered_book: BookRead
    requested_book: BookRead
    status: str
    created_at: datetime
    expires_at: datetime
    responded_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ExchangeOfferUpdate(BaseModel):
    status: ExchangeOfferRole
