# cart.py
# Manages a shopping cart. A cart belongs to one customer and can
# hold multiple items before checkout.
#
# This module knows NOTHING about stock or payments — it is what the
# user sees and interacts with, responsible for building a list of
# intended purchases.

_carts = {}   # { customer_email: { item_id: quantity } }


def add_to_cart(customer_email: str, item_id: str, quantity: int) -> bool:
    """
    Add (or increase) an item in the customer's cart.
    Returns True on success, False if inputs are invalid.
    """
    if not customer_email or "@" not in customer_email:
        return False
    if not item_id or quantity <= 0:
        return False

    cart = _carts.setdefault(customer_email, {})
    cart[item_id] = cart.get(item_id, 0) + quantity
    return True


def remove_from_cart(customer_email: str, item_id: str) -> bool:
    """
    Remove an item entirely from the customer's cart.
    Returns True if the item was present and removed, False otherwise.
    """
    cart = _carts.get(customer_email, {})
    if item_id not in cart:
        return False
    del cart[item_id]
    return True


def get_cart(customer_email: str) -> dict:
    """
    Return a copy of the customer's cart as { item_id: quantity }.
    Returns an empty dict if the customer has no cart.
    """
    return dict(_carts.get(customer_email, {}))


def clear_cart(customer_email: str) -> None:
    """Empty the customer's cart (called after a successful checkout)."""
    _carts.pop(customer_email, None)


def reset_all_carts():
    """Clear all carts. For use in tests only."""
    _carts.clear()
