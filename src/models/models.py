from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Float,
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from src.db.base import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    role = Column(
        Enum("admin", "user", "deliveryman", name="user_roles"),
        nullable=False,
        server_default="user",
    )
    deleted_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)

    carts = relationship("Cart", back_populates="user", uselist=False)


class Cart(Base):
    __tablename__ = "carts"

    id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    user = relationship("User", back_populates="carts")
    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    cart_id = Column(
        Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )

    cart = relationship("Cart", back_populates="cart_items")
    book = relationship("Book", back_populates="cart_items")

    __table_args__ = (UniqueConstraint("cart_id", "book_id", name="uq_cart_book"),)


class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    name = Column(String, unique=True, nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)

    books = relationship("Book", back_populates="category")


class Book(Base):
    __tablename__ = "books"

    id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(
        Enum(
            "available",
            "reserved",
            "in_exchange",
            "exchanged",
            "deleted",
            name="book_status",
        ),
        server_default="True",
        nullable=False,
    )
    thumbnail = Column(String, nullable=False)
    images = Column(JSONB, default=[], nullable=False)
    is_published = Column(Boolean, server_default="False", nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = relationship("Category", back_populates="books")
    cart_items = relationship("CartItem", back_populates="book")


class ExchangeOffer(Base):
    __tablename__ = "exchange_offers"

    id = Column(Integer, primary_key=True)

    from_user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    offered_book_id = Column(ForeignKey("books.id"), nullable=False, index=True)
    requested_book_id = Column(ForeignKey("books.id"), nullable=False, index=True)

    status = Column(
        Enum("pending", "accepted", "declined", "expired", name="offer_status"),
        nullable=False,
        server_default="pending",
        index=True,
    )

    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    expires_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW() + interval '7 days'"),
        nullable=False,
        index=True,
    )

    responded_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)

    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    offered_book = relationship("Book", foreign_keys=[offered_book_id])
    requested_book = relationship("Book", foreign_keys=[requested_book_id])

    __table_args__ = UniqueConstraint(
        "from_user_id",
        "to_user_id",
        "offered_book_id",
        "requested_book_id",
        name="unique_exchange_offer",
    )


class ActiveOrder(Base):
    __tablename__ = "active_orders"

    id = Column(Integer, primary_key=True)

    status = Column(
        Enum(
            "waiting_drop",
            "delivery",
            "waiting_pickup",
            "waiting_cancelled",
            "completed",
            "cancelled",
            name="order_status",
        ),
        nullable=False,
        index=True,
    )

    user1_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    user2_id = Column(ForeignKey("users.id"), nullable=False, index=True)

    user1_book_id = Column(ForeignKey("books.id"), nullable=False, index=True)
    user2_book_id = Column(ForeignKey("books.id"), nullable=False, index=True)

    user1_locker_id = Column(ForeignKey("lockers.id"), nullable=True, index=True)
    user2_locker_id = Column(ForeignKey("lockers.id"), nullable=True, index=True)

    """
    user_status - Обозначение выполнил ли человек свою роль на текущей стадии, положил или забрал ли книгу, 
    при отмене удобно смотреть, если человек не забрал свою книгу а время вышло, в этом время статус поменялся на completed или cancelled. 
    В завершенном ордере, False будет означать что книга в контейнере и нужно ее забирать курьером в склад
    """
    user1_status = Column(Boolean, server_default="False", nullable=False)
    user2_status = Column(Boolean, server_default="False", nullable=False)

    time_deadline = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)
    cancel_reason = Column(
        Enum("delivery_cancel", "user_cancel", "time_cancel", name="cancel_status"),
        nullable=True,
        index=True,
    )

    finished_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)

    user1_book = relationship("Book", foreign_keys=[user1_book_id])
    user2_book = relationship("Book", foreign_keys=[user2_book_id])
    user1_locker = relationship("Locker", foreign_keys=[user1_locker_id])
    user2_locker = relationship("Locker", foreign_keys=[user2_locker_id])

    __table_args__ = UniqueConstraint(
        "user1_id",
        "user2_id",
        "user1_book_id",
        "user2_book_id",
        name="unique_active_orders",
    )


class Locker(Base):
    __tablename__ = "lockers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    available_slots = Column(Integer, nullable=False)

    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    is_active = Column(Boolean, server_default="True", nullable=False)

    __table_args__ = UniqueConstraint("lat", "lng", name="coordinates")
