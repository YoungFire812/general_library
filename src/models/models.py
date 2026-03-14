from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, UniqueConstraint
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    role = Column(Enum("admin", "user", name="user_roles"), nullable=False, server_default="user")
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

    __table_args__ = (
        UniqueConstraint('cart_id', 'book_id', name='uq_cart_book'),
    )

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
    status = Column(Enum("available", "reserved", "in_exchange", "exchanged", "deleted", name="book_status"), server_default="True", nullable=False)
    thumbnail = Column(String, nullable=False)
    images = Column(JSONB, default=[], nullable=False)
    is_published = Column(Boolean, server_default="False", nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
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

    status = Column(Enum("pending", "accepted", "declined", "expired", name="offer_status"), nullable=False, server_default="pending", index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW() + interval '7 days'"), nullable=False, index=True)

    responded_at = Column(TIMESTAMP(timezone=True), server_default=None, nullable=True)

    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

    offered_book = relationship("Book", foreign_keys=[offered_book_id])
    requested_book = relationship("Book", foreign_keys=[requested_book_id])

    __table_args__ = (
        UniqueConstraint(
            "from_user_id",
            "to_user_id",
            "offered_book_id",
            "requested_book_id",
            name="unique_exchange_offer"
        )
    )