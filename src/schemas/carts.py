from pydantic import BaseModel, ConfigDict, HttpUrl


class CartBase(BaseModel):
    user_id: int
    items_count: int

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


class CartCreate(CartBase):
    pass


class CartRead(CartBase):
    id: int


class CartItemBase(BaseModel):
    cart_id: int
    book_id: int

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: int
