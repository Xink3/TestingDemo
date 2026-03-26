# orders.py
# Processes customer orders. Depends on inventory and notifications.

import inventory
import notifications


class OrderResult:
    def __init__(self, success: bool, message: str, order_id: str = None):
        self.success = success
        self.message = message
        self.order_id = order_id

    def __repr__(self):
        return (f"OrderResult(success={self.success}, "
                f"message='{self.message}', order_id='{self.order_id}')")


_order_counter = [1000]


def place_order(customer_email: str, item_id: str, quantity: int) -> (
    OrderResult
):
    """
    Place an order for a given item and quantity.

    Steps:
      1. Validate inputs (email format, quantity > 0)
      2. Check available stock via inventory.get_stock()
      3. Reduce stock via inventory.reduce_stock()
      4. Send a confirmation via notifications.send_confirmation()
      5. Return an OrderResult indicating success or failure
    """
    if not customer_email or "@" not in customer_email:
        return OrderResult(False, "Invalid customer email")

    if quantity <= 0:
        return OrderResult(False, "Quantity must be at least 1")

    available = inventory.get_stock(item_id)
    if available < quantity:
        msg = (f"Insufficient stock: requested {quantity}, "
               f"available {available}")
        return OrderResult(False, msg)

    ok = inventory.reduce_stock(item_id, quantity)
    if not ok:
        return OrderResult(False, "Stock reduction failed unexpectedly")

    _order_counter[0] += 1
    order_id = f"ORD-{_order_counter[0]}"

    notifications.send_confirmation(
        customer_email, order_id, item_id, quantity
    )

    return OrderResult(True, "Order placed successfully", order_id)
