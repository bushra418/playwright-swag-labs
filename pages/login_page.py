from playwright.sync_api import Page, expect


class LoginPage:
    """The Swag Labs sign-in screen.

    Locators are chosen by what the user sees, meaning the placeholder text and
    the button's own label, rather than by CSS class. A class like `.btn_action`
    describes how the page is styled today, so it changes when somebody restyles
    it. The word "Login" on the button only changes when the product changes.
    """

    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.submit = page.get_by_role("button", name="Login")
        self.error = page.locator("[data-test='error']")

    def open(self) -> None:
        self.page.goto(self.URL, wait_until="domcontentloaded")
        expect(self.username).to_be_visible()

    def sign_in(self, user: str, secret: str) -> None:
        self.username.fill(user)
        self.password.fill(secret)
        self.submit.click()

    def error_message(self) -> str:
        """What the page told the user, or "" when it said nothing.

        Returned rather than asserted, so the test decides what counts as
        correct. A page object that asserts makes every caller share one opinion
        about the message.
        """
        if self.error.count() and self.error.first.is_visible():
            return (self.error.first.inner_text() or "").strip()
        return ""
