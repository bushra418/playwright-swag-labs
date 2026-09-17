import re

from playwright.sync_api import Page, expect


class CheckoutPage:
    """Cart, the details form, and the order summary."""

    # `.cart_item` rather than `[data-test='inventory-item']`, which the product
    # list uses as well. A locator that matches on both pages cannot tell which
    # one it is looking at: read a moment early and it finds six products on the
    # page being left and reports them as the cart's contents, with nothing
    # about it looking wrong. `.cart_item` exists only here, so an early read
    # finds nothing and waits instead of lying.
    ITEM = ".cart_item"

    def __init__(self, page: Page):
        self.page = page
        self.cart_items = page.locator(self.ITEM)
        self.checkout = page.get_by_role("button", name="Checkout")
        self.first_name = page.get_by_placeholder("First Name")
        self.last_name = page.get_by_placeholder("Last Name")
        self.postal_code = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button = page.locator("[data-test='continue']")
        self.finish = page.get_by_role("button", name="Finish")
        self.error = page.locator("[data-test='error']")

    def item_names(self) -> list:
        """The products in the cart.

        Read in one call rather than counting the rows and then asking for each
        one by index. `count()` does not wait for anything, so a loop built on
        it can take its count from the page it is leaving and then index into
        the page it has arrived at. That failed here exactly once, in CI, asking
        for the sixth row of a cart holding two.
        """
        expect(self.cart_items.first).to_be_visible()
        return [
            text.strip()
            for text in self.cart_items.locator(".inventory_item_name").all_inner_texts()
        ]

    def start_checkout(self) -> None:
        self.checkout.click()
        expect(self.first_name).to_be_visible()

    def fill_details(self, first: str = "", last: str = "", postcode: str = "") -> None:
        """Fill the form. Any field can be left blank, to test what is required."""
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(postcode)

    def continue_to_summary(self) -> None:
        self.continue_button.click()

    def error_message(self) -> str:
        if self.error.count() and self.error.first.is_visible():
            return (self.error.first.inner_text() or "").strip()
        return ""

    def summary_total(self) -> float:
        """The item total before tax, as a number."""
        text = self.page.locator(".summary_subtotal_label").inner_text() or ""
        found = re.search(r"[\d.]+", text)
        assert found, f"No subtotal found in {text!r}"
        return float(found.group())

    def complete_order(self) -> str:
        self.finish.click()
        header = self.page.locator(".complete-header")
        expect(header).to_be_visible()
        return (header.inner_text() or "").strip()
