import re

from playwright.sync_api import Page, expect


class InventoryPage:
    """The product list, and the cart badge that tracks it."""

    ITEM = "[data-test='inventory-item']"

    def __init__(self, page: Page):
        self.page = page
        self.items = page.locator(self.ITEM)
        self.cart_link = page.locator(".shopping_cart_link")
        self.sort = page.locator("[data-test='product-sort-container']")

    def wait_until_loaded(self) -> None:
        expect(self.items.first).to_be_visible()

    def product_names(self) -> list:
        """Every product name, read in one call.

        Not a loop over `count()`. That call does not wait, so a loop built on
        it can count the rows of one page and then index into another if the
        browser is navigating underneath it.
        """
        return [
            text.strip()
            for text in self.items.locator(".inventory_item_name").all_inner_texts()
        ]

    def prices(self) -> list:
        """Prices as numbers, so a test can compare them rather than their text.

        Sorted "$100.00" and "$9.99" compare the wrong way round as strings, so
        a string comparison would call a correctly sorted page broken.
        """
        values = []
        for text in self.items.locator(".inventory_item_price").all_inner_texts():
            found = re.search(r"[\d.]+", text)
            if found:
                values.append(float(found.group()))
        return values

    def add_to_cart(self, product: str) -> None:
        item = self.items.filter(has_text=product).first
        expect(item).to_be_visible()
        item.get_by_role("button", name=re.compile("add to cart", re.I)).click()

    def remove_from_cart(self, product: str) -> None:
        item = self.items.filter(has_text=product).first
        item.get_by_role("button", name=re.compile("remove", re.I)).click()

    def cart_count(self) -> int:
        """How many items the cart badge claims.

        The badge is absent rather than zero when the cart is empty, so its
        absence is read as 0 instead of failing to find an element.
        """
        badge = self.page.locator(".shopping_cart_badge")
        if not badge.count():
            return 0
        return int((badge.first.inner_text() or "0").strip() or 0)

    def sort_by(self, label: str) -> None:
        self.sort.select_option(label=label)
        self.page.wait_for_timeout(300)

    def open_cart(self) -> None:
        """Open the cart and wait until the browser is actually there.

        Without the wait, a caller that counts the rows straight away counts
        the six products still on screen, then asks for the third one after the
        cart has replaced them with two. The failure arrives as a timeout on an
        element, which says nothing about the navigation that caused it.
        """
        self.cart_link.click()
        self.page.wait_for_url(re.compile(r"cart\.html"))
