# STEP 2 — Feature / Functional Tests: Checkout feature
#
# We test the COMPLETE "Place Order" flow:
#   cart → checkout → order confirmed → cart cleared
#
# Differences from unit tests:
# - NO mocking; all real modules are used.
# - Tests are based on requirements, not functions.
# - Black-box testing (only inputs/outputs).

import cart
import inventory
import notifications
import checkout


# ── Shared setup ──────────────────────────────────────────────────────────
def setup_function():
    inventory.reset_stock()
    notifications.clear()
    cart.reset_all_carts()


# REQUIREMENT 1
# Customer with items can checkout successfully.

class TestCheckoutHappyPath:

    def test_checkout_single_item_succeeds(self):
        """
        PRE: 1 item in cart, in stock
        ACT: checkout
        POST: success with one order ID
        """
        cart.add_to_cart("alice@example.com", "laptop", 2)

        result = checkout.checkout("alice@example.com")

        assert result.success is True
        assert len(result.order_ids) == 1

    def test_checkout_clears_cart_on_success(self):
        cart.add_to_cart("alice@example.com", "mouse", 5)

        checkout.checkout("alice@example.com")

        assert cart.get_cart("alice@example.com") == {}

    def test_checkout_multi_item_cart_succeeds(self):
        cart.add_to_cart("bob@example.com", "laptop", 1)
        cart.add_to_cart("bob@example.com", "mouse", 3)
        cart.add_to_cart("bob@example.com", "keyboard", 2)

        result = checkout.checkout("bob@example.com")

        assert result.success is True
        assert len(result.order_ids) == 3

    def test_checkout_reduces_stock_for_all_items(self):
        cart.add_to_cart("carol@example.com", "laptop", 2)
        cart.add_to_cart("carol@example.com", "mouse", 10)

        checkout.checkout("carol@example.com")

        assert inventory.get_stock("laptop") == 8
        assert inventory.get_stock("mouse") == 40

    def test_checkout_sends_confirmation_per_item(self):
        cart.add_to_cart("dana@example.com", "laptop", 1)
        cart.add_to_cart("dana@example.com", "keyboard", 1)

        checkout.checkout("dana@example.com")

        sent = notifications.get_sent()
        assert len(sent) == 2
        assert all(n["email"] == "dana@example.com" for n in sent)


# REQUIREMENT 2
# Cannot checkout with empty cart.

class TestCheckoutEmptyCart:

    def test_checkout_with_empty_cart_fails(self):
        result = checkout.checkout("ed@example.com")

        assert result.success is False
        assert "empty" in result.message.lower()

    def test_checkout_empty_cart_sends_no_notification(self):
        result = checkout.checkout("ed@example.com")

        assert result.success is False
        assert len(notifications.get_sent()) == 0


# REQUIREMENT 3
# Partial failure when some items are out of stock.

class TestCheckoutPartialFailure:

    def test_out_of_stock_item_causes_partial_failure(self):
        cart.add_to_cart("frank@example.com", "laptop", 1)
        cart.add_to_cart(
            "frank@example.com", "hoverboard", 1
        )  # not stocked

        result = checkout.checkout("frank@example.com")

        assert result.success is False
        assert len(result.order_ids) == 1
        assert len(result.failures) == 1
        assert result.failures[0]["item_id"] == "hoverboard"

    def test_failed_item_stays_in_cart_after_partial_checkout(self):
        cart.add_to_cart("frank@example.com", "mouse", 3)
        cart.add_to_cart("frank@example.com", "hoverboard", 1)

        checkout.checkout("frank@example.com")

        remaining = cart.get_cart("frank@example.com")
        assert "hoverboard" in remaining
        assert "mouse" not in remaining

    def test_successful_items_stock_reduced_on_partial_failure(self):
        cart.add_to_cart("grace@example.com", "keyboard", 5)
        cart.add_to_cart("grace@example.com", "hoverboard", 1)

        checkout.checkout("grace@example.com")

        assert inventory.get_stock("keyboard") == 20

    def test_requesting_more_than_stock_causes_failure(self):
        cart.add_to_cart("heidi@example.com", "laptop", 999)

        result = checkout.checkout("heidi@example.com")

        assert result.success is False
        assert len(result.failures) == 1
        assert "stock" in result.failures[0]["reason"].lower()


# REQUIREMENT 4
# Invalid inputs rejected before processing.

class TestCheckoutInputValidation:

    def test_invalid_email_is_rejected(self):
        cart._carts["notanemail"] = {"laptop": 1}

        result = checkout.checkout("notanemail")

        assert result.success is False
        assert inventory.get_stock("laptop") == 10
        assert len(notifications.get_sent()) == 0

    def test_two_customers_carts_are_independent(self):
        cart.add_to_cart("alice@example.com", "laptop", 1)
        cart.add_to_cart("bob@example.com", "mouse", 5)

        checkout.checkout("alice@example.com")

        bob_cart = cart.get_cart("bob@example.com")
        assert bob_cart == {"mouse": 5}
