# STEP 3 — Integration Tests: orders + inventory + notifications
# No mocking. Real modules are wired together.
# We verify they collaborate correctly.

# Difference from unit tests:
# - Unit tests used mocks
# - Integration tests use REAL modules

import inventory
import notifications
import orders


# ── Shared setup ──────────────────────────────────────────────────────────
def setup_function():
    inventory.reset_stock()
    notifications.clear()


# ── orders ↔ inventory ────────────────────────────────────────────────────
class TestOrdersInventoryIntegration:

    def test_successful_order_reduces_stock(self):
        before = inventory.get_stock("mouse")
        orders.place_order("alice@example.com", "mouse", 3)
        after = inventory.get_stock("mouse")

        assert after == before - 3

    def test_order_for_unavailable_item_leaves_stock_unchanged(self):
        orders.place_order("alice@example.com", "laptop", 999)
        assert inventory.get_stock("laptop") == 10

    def test_two_sequential_orders_accumulate_correctly(self):
        orders.place_order("a@a.com", "keyboard", 5)
        orders.place_order("b@b.com", "keyboard", 10)

        assert inventory.get_stock("keyboard") == 10

    def test_ordering_exact_remaining_stock_empties_item(self):
        """
        Edge case: ordering exactly what's left should succeed.
        """
        available = inventory.get_stock("laptop")

        result = orders.place_order(
            "dana@example.com", "laptop", available
        )

        assert result.success is True, (
            "Order should succeed when requesting exact stock.\n"
            "Check reduce_stock() when stock hits zero."
        )

        assert inventory.get_stock("laptop") == 0


# ── orders ↔ notifications ────────────────────────────────────────────────
class TestOrdersNotificationsIntegration:

    def test_successful_order_sends_one_notification(self):
        orders.place_order("bob@example.com", "keyboard", 2)

        sent = notifications.get_sent()
        assert len(sent) == 1

    def test_notification_contains_correct_email(self):
        orders.place_order("carol@example.com", "mouse", 1)

        sent = notifications.get_sent()
        assert sent[0]["email"] == "carol@example.com"

    def test_notification_contains_correct_item_and_quantity(self):
        orders.place_order("carol@example.com", "mouse", 4)

        sent = notifications.get_sent()
        assert sent[0]["item_id"] == "mouse"
        assert sent[0]["quantity"] == 4

    def test_notification_order_id_matches_result(self):
        result = orders.place_order("ed@example.com", "mouse", 1)

        sent = notifications.get_sent()
        assert sent[0]["order_id"] == result.order_id

    def test_failed_order_sends_no_notification(self):
        orders.place_order("ghost@example.com", "laptop", 9999)

        assert len(notifications.get_sent()) == 0

    def test_two_orders_send_two_notifications(self):
        orders.place_order("a@a.com", "mouse", 1)
        orders.place_order("b@b.com", "mouse", 1)

        sent = notifications.get_sent()
        assert len(sent) == 2
        assert sent[0]["email"] != sent[1]["email"]


# ── Full end-to-end flow ──────────────────────────────────────────────────
class TestFullOrderFlow:

    def test_complete_happy_path(self):
        """
        Validate full flow:
        - success result
        - stock reduced
        - notification sent
        """
        result = orders.place_order(
            "frank@example.com", "laptop", 3
        )

        # Order result
        assert result.success is True
        assert result.order_id is not None

        # Inventory effect
        assert inventory.get_stock("laptop") == 7

        # Notification effect
        sent = notifications.get_sent()
        assert len(sent) == 1
        assert sent[0]["email"] == "frank@example.com"
        assert sent[0]["order_id"] == result.order_id
        assert sent[0]["item_id"] == "laptop"
        assert sent[0]["quantity"] == 3
