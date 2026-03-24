# inventory.py
# Manages stock levels for the order system.

_stock = {
    "laptop": 10,
    "mouse": 50,
    "keyboard": 25,
}


def get_stock(item_id: str) -> int:
    """Return current stock count for an item. Returns 0 if the item is unknown."""
    return _stock.get(item_id, 0)


def reduce_stock(item_id: str, quantity: int) -> bool:
    """
    Reduce stock by quantity.
    Returns True on success, False if there is insufficient stock.
    Raises ValueError if quantity is not a positive integer.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be a positive integer")
    current = _stock.get(item_id, 0)
    if current < quantity:
        return False
    _stock[item_id] = current - quantity
    return _stock[item_id]


def reset_stock():
    """Reset stock to default values. Call this in test setUp/teardown."""
    _stock.clear()
    _stock.update({"laptop": 10, "mouse": 50, "keyboard": 25})
