# notifications.py
# Handles confirmation messages for completed orders.
# In a real system this would call an email/SMS API.

_sent = []


def send_confirmation(email: str, order_id: str,
                      item_id: str, quantity: int) -> None:
    """
    Record a confirmation notification.
    Simulates sending an email.
    """
    record = {
        "email": email,
        "order_id": order_id,
        "item_id": item_id,
        "quantity": quantity,
    }
    _sent.append(record)
    print(
        f"[NOTIFICATION] Confirmation sent → {email} "
        f"(order: {order_id})"
    )


def get_sent() -> list:
    """Return all notifications sent so far. Useful in tests."""
    return list(_sent)


def clear():
    """Clear notification history. Call this in test setUp/teardown."""
    _sent.clear()
