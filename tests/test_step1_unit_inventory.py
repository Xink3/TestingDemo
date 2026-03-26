# STEP 1 — Unit Tests: inventory module
# Test each function IN ISOLATION. No orders, no notifications.
# Every test follows the same three-part pattern:
#   ARRANGE – set up the starting state
#   ACT     – call the function under test
#   ASSERT  – check the result

import pytest
import inventory


# ── Shared setup ──────────────────────────────────────────────────────────
# Before each test, reset stock to known defaults so tests don't
# affect each other. pytest calls setup_function() automatically.

def setup_function():
    inventory.reset_stock()


# ── get_stock() ───────────────────────────────────────────────────────────
class TestGetStock:
    def test_returns_correct_count_for_known_item(self):
        # ARRANGE: stock was reset to defaults (laptop = 10)
        result = inventory.get_stock("laptop")
        assert result == 10

    def test_returns_zero_for_unknown_item(self):
        result = inventory.get_stock("hoverboard")
        assert result == 0

    def test_returns_correct_count_for_mouse(self):
        result = inventory.get_stock("mouse")
        assert result == 50

    def test_returns_correct_count_for_keyboard(self):
        result = inventory.get_stock("keyboard")
        assert result == 25


# ── reduce_stock() ────────────────────────────────────────────────────────
class TestReduceStock:
    def test_happy_path_returns_true(self):
        result = inventory.reduce_stock("laptop", 3)
        assert result is True

    def test_happy_path_stock_is_decremented(self):
        inventory.reduce_stock("laptop", 3)
        assert inventory.get_stock("laptop") == 7

    def test_reduce_all_stock_returns_true(self):
        result = inventory.reduce_stock("laptop", 10)
        assert result is True

    def test_reduce_all_stock_leaves_zero(self):
        inventory.reduce_stock("laptop", 10)
        assert inventory.get_stock("laptop") == 0

    def test_insufficient_stock_returns_false(self):
        # Request more than available (laptop = 10, requesting 11)
        result = inventory.reduce_stock("laptop", 11)
        assert result is False

    def test_insufficient_stock_does_not_change_count(self):
        inventory.reduce_stock("laptop", 11)
        assert inventory.get_stock("laptop") == 10  # still 10

    def test_unknown_item_returns_false(self):
        result = inventory.reduce_stock("hoverboard", 1)
        assert result is False

    def test_zero_quantity_raises_value_error(self):
        with pytest.raises(ValueError):
            inventory.reduce_stock("laptop", 0)

    def test_negative_quantity_raises_value_error(self):
        with pytest.raises(ValueError):
            inventory.reduce_stock("laptop", -5)

    def test_multiple_reductions_accumulate_correctly(self):
        inventory.reduce_stock("mouse", 10)  # 50 → 40
        inventory.reduce_stock("mouse", 15)  # 40 → 25
        assert inventory.get_stock("mouse") == 25
