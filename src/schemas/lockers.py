from pydantic import BaseModel, ConfigDict


class LockerCreate(BaseModel):
    name: str
    address: str
    available_slots: int
    lat: float
    lng: float


class LockerRead(BaseModel):
    id: int
    name: str
    address: str
    available_slots: int
    lat: float
    lng: float

    model_config = ConfigDict(from_attributes=True)


class LockerRequest(BaseModel):
    locker_id: int
