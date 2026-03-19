from pydantic import BaseModel, ConfigDict


class CartBase(BaseModel):
    user_id: int


class CartCreate(CartBase):
    pass


class CartRead(CartBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CartItemBase(BaseModel):
    cart_id: int
    book_id: int


class CartItemCreate(CartItemBase):
    pass


class CartItemRead(CartItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
