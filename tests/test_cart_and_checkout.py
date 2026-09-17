import pytest

from pages.checkout_page import CheckoutPage


def test_adding_and_removing_keeps_the_badge_honest(signed_in):
    """The cart badge must follow what is actually in the cart.

    Checked in both directions. A badge that counts up correctly but never
    counts down is a real defect, and a test that only ever adds would pass
    against it.
    """
    products = signed_in.product_names()
    assert len(products) >= 2, "Need at least two products to test the cart"

    assert signed_in.cart_count() == 0, (
        f"The cart should start empty, but the badge shows {signed_in.cart_count()}"
    )

    signed_in.add_to_cart(products[0])
    assert signed_in.cart_count() == 1, "Adding one product did not show 1 in the badge"

    signed_in.add_to_cart(products[1])
    assert signed_in.cart_count() == 2, "Adding a second product did not show 2"

    signed_in.remove_from_cart(products[0])
    assert signed_in.cart_count() == 1, (
        f"After removing one of two products the badge shows "
        f"{signed_in.cart_count()}, not 1"
    )


def test_the_cart_holds_what_was_chosen(signed_in, page):
    """What reaches the cart is what was added, not merely the right number.

    Counting alone would pass if the page added the wrong product, which is why
    the names are compared rather than the total.
    """
    products = signed_in.product_names()
    chosen = [products[0], products[2]] if len(products) > 2 else products[:2]

    for product in chosen:
        signed_in.add_to_cart(product)
    signed_in.open_cart()

    in_cart = CheckoutPage(page).item_names()
    assert sorted(in_cart) == sorted(chosen), (
        f"Added {chosen} but the cart holds {in_cart}"
    )


@pytest.mark.parametrize(
    "first, last, postcode, missing",
    [
        ("", "Jamil", "46000", "first name"),
        ("Bushra", "", "46000", "last name"),
        ("Bushra", "Jamil", "", "postcode"),
    ],
)
def test_checkout_requires_every_detail(signed_in, page, first, last, postcode, missing):
    """Each field on the details form is required, and proven so one at a time.

    Submitting an entirely blank form would prove only that *something* is
    required. Leaving out one field at a time is what shows each is enforced.
    """
    signed_in.add_to_cart(signed_in.product_names()[0])
    signed_in.open_cart()

    checkout = CheckoutPage(page)
    checkout.start_checkout()
    checkout.fill_details(first, last, postcode)
    checkout.continue_to_summary()

    assert "step-two" not in page.url, (
        f"Checkout continued without a {missing}"
    )
    assert checkout.error_message(), (
        f"Checkout was blocked without a {missing}, but the form gave no reason"
    )


def test_an_order_can_be_placed_and_the_total_adds_up(signed_in, page):
    """The happy path, with the arithmetic checked rather than assumed.

    A summary that lists the right products but totals them wrongly is the kind
    of defect that reaches customers, and no click-through test notices it.
    """
    products = signed_in.product_names()[:2]
    for product in products:
        signed_in.add_to_cart(product)

    prices = dict(zip(signed_in.product_names(), signed_in.prices()))
    expected_total = round(sum(prices[p] for p in products), 2)

    signed_in.open_cart()
    checkout = CheckoutPage(page)
    checkout.start_checkout()
    checkout.fill_details("Bushra", "Jamil", "46000")
    checkout.continue_to_summary()

    assert checkout.summary_total() == expected_total, (
        f"The order lists {products}, which cost {expected_total}, but the "
        f"summary totals {checkout.summary_total()}"
    )

    confirmation = checkout.complete_order()
    assert "thank you" in confirmation.lower(), (
        f"Completing the order showed {confirmation!r} rather than a confirmation"
    )
