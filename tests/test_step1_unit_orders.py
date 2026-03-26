# STEP 1 — Unit Tests: orders module
# We test place_order() IN ISOLATION by mocking dependencies.
# inventory and notifications are replaced so we only test
# ORDER logic.

# KEY CONCEPT: unittest.mock.patch temporarily replaces a real
# module with a controlled fake ("mock") during a test.

from unittest.mock import patch, MagicMock
import orders


# ── Helper: fake inventory functions ──────────────────────────────────────
def _mock_inventory(stock_value=10, reduce_returns=True):
    """
    Create mock inventory functions.

    stock_value: value returned by get_stock()
    reduce_returns: value returned by reduce_stock()
    """
    mock_get = MagicMock(return_value=stock_value)
    mock_reduce = MagicMock(return_value=reduce_returns)
    return mock_get, mock_reduce


# ── Input validation tests ────────────────────────────────────────────────
class TestPlaceOrderValidation:

    def test_missing_email_returns_failure(self):
        result = orders.place_order("", "laptop", 1)
        assert result.success is False

    def test_email_without_at_sign_returns_failure(self):
        result = orders.place_order("notanemail", "laptop", 1)
        assert result.success is False

    def test_zero_quantity_returns_failure(self):
        result = orders.place_order("a@b.com", "laptop", 0)
        assert result.success is False

    def test_negative_quantity_returns_failure(self):
        result = orders.place_order("a@b.com", "laptop", -3)
        assert result.success is False


# ── Business logic tests (inventory mocked) ───────────────────────────────
class TestPlaceOrderLogic:

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_order_succeeds_when_stock_available(self, mock_notif, mock_inv):
        # ARRANGE
        mock_inv.get_stock.return_value = 10
        mock_inv.reduce_stock.return_value = True

        # ACT
        result = orders.place_order(
            "alice@example.com", "laptop", 2
        )

        # ASSERT
        assert result.success is True

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_order_fails_when_stock_insufficient(
        self, mock_notif, mock_inv
    ):
        # ARRANGE
        mock_inv.get_stock.return_value = 1

        # ACT
        result = orders.place_order(
            "alice@example.com", "laptop", 5
        )

        # ASSERT
        assert result.success is False
        mock_inv.reduce_stock.assert_not_called()

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_successful_order_calls_reduce_stock(
        self, mock_notif, mock_inv
    ):
        mock_inv.get_stock.return_value = 10
        mock_inv.reduce_stock.return_value = True

        orders.place_order("alice@example.com", "laptop", 3)

        mock_inv.reduce_stock.assert_called_once_with(
            "laptop", 3
        )

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_successful_order_calls_send_confirmation(
        self, mock_notif, mock_inv
    ):
        mock_inv.get_stock.return_value = 10
        mock_inv.reduce_stock.return_value = True

        result = orders.place_order(
            "alice@example.com", "laptop", 3
        )

        mock_notif.send_confirmation.assert_called_once()

        args = mock_notif.send_confirmation.call_args[0]
        assert args[0] == "alice@example.com"
        assert args[1] == result.order_id

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_failed_order_does_not_send_notification(
        self, mock_notif, mock_inv
    ):
        mock_inv.get_stock.return_value = 0

        orders.place_order("alice@example.com", "laptop", 1)

        mock_notif.send_confirmation.assert_not_called()

    @patch("orders.inventory")
    @patch("orders.notifications")
    def test_successful_order_has_unique_order_id(
        self, mock_notif, mock_inv
    ):
        mock_inv.get_stock.return_value = 100
        mock_inv.reduce_stock.return_value = True

        result1 = orders.place_order("a@a.com", "laptop", 1)
        result2 = orders.place_order("b@b.com", "laptop", 1)

        assert result1.order_id != result2.order_id
