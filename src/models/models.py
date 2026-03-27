from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Float,
    Index
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from src.db.base import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("admin", "user", "deliveryman", name="user_roles"),
        nullable=False,
        server_default=text("'user'"),
        index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, index=True)

    carts: Mapped["Cart"] = relationship("Cart", back_populates="user", uselist=False)


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="carts")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    cart_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )

    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    book: Mapped["Book"] = relationship("Book", back_populates="cart_items")

    __table_args__ = (UniqueConstraint("cart_id", "book_id", name="uq_cart_book"),)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, index=True)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="category")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(
        Enum(
            "available",
            "reserved",
            "in_exchange",
            "exchanged",
            "deleted",
            name="book_status",
        ),
        server_default=text("'available'"),
        nullable=False,
        index=True
    )

    thumbnail: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[list] = mapped_column(JSONB, default=list, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    category: Mapped["Category"] = relationship("Category", back_populates="books")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="book")

    __table_args__ = (
        Index("idx_books_title", "title"),
        Index("idx_books_author", "author"),
    )


class ExchangeOffer(Base):
    __tablename__ = "exchange_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    from_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    offered_book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    requested_book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "declined", "expired", name="offer_status"),
        nullable=False,
        server_default=text("'pending'"),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW() + interval '7 days'"),
        nullable=False,
        index=True,
    )

    responded_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, index=True)

    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id])
    offered_book: Mapped["Book"] = relationship("Book", foreign_keys=[offered_book_id])
    requested_book: Mapped["Book"] = relationship("Book", foreign_keys=[requested_book_id])

    __table_args__ = (
        UniqueConstraint(
            "from_user_id",
            "to_user_id",
            "offered_book_id",
            "requested_book_id",
            name="unique_exchange_offer",
        ),
    )


class ActiveOrder(Base):
    __tablename__ = "active_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    status: Mapped[str] = mapped_column(
        Enum(
            "waiting_drop",
            "delivery",
            "waiting_pickup",
            "waiting_cancelled",
            "completed",
            "cancelled",
            name="order_status",
        ),
        server_default=text("'waiting_drop'"),
        nullable=False,
        index=True,
    )

    user1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    user1_book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    user2_book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False, index=True)

    user1_locker_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("lockers.id"), nullable=True, index=True)
    user2_locker_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("lockers.id"), nullable=True, index=True)

    """
    user_status - Обозначение выполнил ли человек свою роль на текущей стадии, положил или забрал ли книгу, 
    при отмене удобно смотреть, если человек не забрал свою книгу а время вышло, в этом время статус поменялся на completed или cancelled. 
    В завершенном ордере, False будет означать что книга в контейнере и нужно ее забирать курьером в склад
    """
    user1_status: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    user2_status: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)

    time_deadline: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("NOW() + interval '7 days'"), nullable=False)
    cancel_reason: Mapped[str | None] = mapped_column(
        Enum("delivery_cancel", "user_cancel", "time_cancel", name="cancel_status"),
        nullable=True,
        index=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, index=True)

    user1_book: Mapped["Book"] = relationship("Book", foreign_keys=[user1_book_id])
    user2_book: Mapped["Book"] = relationship("Book", foreign_keys=[user2_book_id])
    user1_locker: Mapped["Locker"] = relationship("Locker", foreign_keys=[user1_locker_id])
    user2_locker: Mapped["Locker"] = relationship("Locker", foreign_keys=[user2_locker_id])

    __table_args__ = (
        UniqueConstraint(
            "user1_id",
            "user2_id",
            "user1_book_id",
            "user2_book_id",
            name="unique_active_orders",
        ),
        Index(
            "idx_active_orders_status_timedeadline_id",
            "status",
            "time_deadline",
            "id",
        )
    )


class Locker(Base):
    __tablename__ = "lockers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String, nullable=False, index=True)
    available_slots: Mapped[int] = mapped_column(Integer, nullable=False)

    lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    lng: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("lat", "lng", name="coordinates"),
        Index("idx_lockers_lat_lng", "lat", "lng")
    )
