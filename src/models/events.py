from sqlalchemy import event, update
from src.models.models import CartItem, Cart, Book, Category


# работа с CartItem
@event.listens_for(CartItem, "after_insert")
def update_cart_total_amount(mapper, connection, target: CartItem):
    connection.execute(
        update(Cart)
        .where(Cart.id == target.cart_id)
        .values(items_count=Cart.items_count + 1)
    )


@event.listens_for(CartItem, "after_delete")
def update_cart_total_amount_after_delete(mapper, connection, target: CartItem):
    connection.execute(
        update(Cart)
        .where(Cart.id == target.cart_id)
        .values(items_count=Cart.items_count - 1)
    )


# работа с Book
@event.listens_for(Book, "after_insert")
def update_cart_total_amount_after_delete(mapper, connection, target: CartItem):
    connection.execute(
        update(Category)
        .where(Category.id == target.category_id)
        .values(items_count=Category.items_count + 1)
    )


@event.listens_for(Book, "after_delete")
def update_cart_total_amount_after_delete(mapper, connection, target: CartItem):
    connection.execute(
        update(Category)
        .where(Category.id == target.category_id)
        .values(items_count=Category.items_count - 1)
    )
