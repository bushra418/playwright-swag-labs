import re

from playwright.sync_api import Page, expect


class CheckoutPage:
    """Cart, the details form, and the order summary."""

    def __init__(self, page: Page):
        self.page = page
        self.cart_items = page.locator("[data-test='inventory-item']")
        self.checkout = page.get_by_role("button", name="Checkout")
        self.first_name = page.get_by_placeholder("First Name")
        self.last_name = page.get_by_placeholder("Last Name")
        self.postal_code = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button = page.locator("[data-test='continue']")
        self.finish = page.get_by_role("button", name="Finish")
        self.error = page.locator("[data-test='error']")

    def item_names(self) -> list:
        return [
            (self.cart_items.nth(i).locator(".inventory_item_name").inner_text() or "").strip()
            for i in range(self.cart_items.count())
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
