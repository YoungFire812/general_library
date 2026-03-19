from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Literal


class OrderStatus(Enum):
    waiting_drop = ("waiting_drop",)
    delivery = ("delivery",)
    waiting_pickup = ("waiting_pickup",)
    waiting_cancelled = ("waiting_cancelled",)
    completed = ("completed",)
    cancelled = ("cancelled",)


class CancelReason(str, Enum):
    delivery_cancel = "delivery_cancel"
    user_cancel = "user_cancel"


class CancelOrderRequest(BaseModel):
    cancel_reason: CancelReason


class ActiveOrderCreate(BaseModel):
    status: Literal["waiting_drop"] = "waiting_drop"

    user1_id: int
    user2_id: int

    user1_book_id: int
    user2_book_id: int

    user1_status: Literal[False] = False
    user2_status: Literal[False] = False

    user1_locker_id: Literal[None] = None
    user2_locker_id: Literal[None] = None

    time_deadline: datetime | None = None

    def model_post_init(self, __context=None):
        self.time_deadline = datetime.now(timezone.utc) + timedelta(days=7)


class ActiveOrderRead(BaseModel):
    id: int

    status: OrderStatus

    user1_id: int
    user2_id: int

    user1_book_id: int
    user2_book_id: int

    user1_locker_id: int | None
    user2_locker_id: int | None

    user1_status: bool
    user2_status: bool

    time_deadline: datetime

    model_config = ConfigDict(from_attributes=True)
