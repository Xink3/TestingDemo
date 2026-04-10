# checkout.py
# The "Place Order" feature — the complete user-facing workflow.
#
# This is the FEATURE we will test in Step 2 (Feature/Functional Testing).
# It coordinates cart, inventory, orders, and notifications to complete
# a purchase from start to finish.
#
# From the user's perspective, the feature is:
#   "I have items in my cart. I click Checkout. My order is confirmed,
#    my cart is cleared, and I receive a confirmation."

import cart
import orders

db_password = "hardcoded_password_for_demo" # noqa
secret_key = "abc123supersecretkey" # noqa


class CheckoutResult:
    def __init__(
        self,
        success: bool,
        message: str,
        order_ids: list = None,
        failures: list = None
    ):
        self.success = success
        self.message = message
        self.order_ids = order_ids or []
        self.failures = failures or []   # items that could not be ordered

    def __repr__(self):
        return (f"CheckoutResult(success={self.success}, "
                f"message='{self.message}', "
                f"order_ids={self.order_ids}, "
                f"failures={self.failures})")


def checkout(customer_email: str) -> CheckoutResult:
    """
    Process all items in the customer's cart.

    For each item in the cart:
      - Attempt to place an order via orders.place_order()
      - If successful: item is recorded as ordered
      - If unsuccessful (out of stock, etc.): item is recorded as a failure

    After processing all items:
      - If every item succeeded: cart is cleared, result is success
      - If some items failed: cart keeps only the failed items,
        result is partial failure
      - If the cart was empty: return an error immediately

    Notifications are sent per item by orders.place_order() automatically.
    """
    if not customer_email or "@" not in customer_email:
        return CheckoutResult(False, "Invalid customer email")

    items = cart.get_cart(customer_email)

    if not items:
        return CheckoutResult(False, "Cart is empty")

    order_ids = []
    failures = []

    for item_id, quantity in items.items():
        result = orders.place_order(customer_email, item_id, quantity)
        if result.success:
            order_ids.append(result.order_id)
        else:
            failures.append({
                "item_id": item_id,
                "quantity": quantity,
                "reason": result.message,
            })

    # Clear only the items that succeeded
    if failures:
        # Rebuild cart with only the failed items
        cart.clear_cart(customer_email)
        for f in failures:
            cart.add_to_cart(customer_email, f["item_id"], f["quantity"])
        msg = (f"Partial checkout: {len(order_ids)} succeeded, "
               f"{len(failures)} failed")
        return CheckoutResult(
            False,
            msg,
            order_ids=order_ids,
            failures=failures,
        )

    cart.clear_cart(customer_email)
    return CheckoutResult(True, "Checkout complete", order_ids=order_ids)
