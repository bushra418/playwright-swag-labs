import pytest

from conftest import LOCKED_OUT_USER, STANDARD_PASS, STANDARD_USER
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_valid_credentials_reach_the_product_list(page):
    login = LoginPage(page)
    login.open()
    login.sign_in(STANDARD_USER, STANDARD_PASS)

    InventoryPage(page).wait_until_loaded()
    assert "inventory" in page.url, (
        f"Signing in as {STANDARD_USER} should open the product list, but the "
        f"browser is at {page.url}"
    )


@pytest.mark.parametrize(
    "user, secret, because",
    [
        ("", "secret_sauce", "no username"),
        ("standard_user", "", "no password"),
        ("standard_user", "wrong_password", "the wrong password"),
        ("no_such_user", "secret_sauce", "an unknown username"),
    ],
)
def test_bad_credentials_are_refused_and_explained(page, user, secret, because):
    """A rejected sign-in must say so, and must not let the user through.

    Both halves matter. A page that stays put without a message leaves the user
    guessing, and a page that shows a message while still signing them in is
    worse than either.
    """
    login = LoginPage(page)
    login.open()
    login.sign_in(user, secret)

    assert "inventory" not in page.url, (
        f"Signing in with {because} was accepted - the browser reached {page.url}"
    )
    assert login.error_message(), (
        f"Signing in with {because} was refused, but the page gave no reason"
    )


def test_a_locked_out_account_is_told_why(page):
    """The message has to name the cause, not just fail.

    "Username and password do not match" would be wrong here and would send the
    user to reset a password that is not the problem.
    """
    login = LoginPage(page)
    login.open()
    login.sign_in(LOCKED_OUT_USER, STANDARD_PASS)

    message = login.error_message()
    assert message, "A locked-out account was refused without any message"
    assert "locked" in message.lower(), (
        f"A locked-out account should be told the account is locked. It was "
        f"told: {message!r}"
    )
