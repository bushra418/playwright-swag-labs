"""Fixtures, and the evidence a failure leaves behind."""

import os
import re
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from config import STANDARD_PASS, STANDARD_USER

EVIDENCE = Path(__file__).resolve().parent / "reports" / "failures"


@pytest.fixture(scope="session")
def browser():
    """One browser per session. Headed locally, headless in CI.

    CI has no display, so it sets HEADLESS=1. Locally the default is a visible
    window, because watching a run is how you notice the things an assertion
    was never written to catch.
    """
    with sync_playwright() as p:
        chromium = p.chromium.launch(headless=os.environ.get("HEADLESS", "0") == "1")
        yield chromium
        chromium.close()


@pytest.fixture
def page(browser):
    """A fresh context per test, so no test inherits another's session."""
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.set_default_timeout(15000)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def signed_in(page):
    """Signed in as the standard user, on the product list.

    Most tests are about something other than signing in, and repeating the
    login in each of them would mean a change to the login screen breaking
    every test in the suite rather than the one that covers it.
    """
    from pages.inventory_page import InventoryPage
    from pages.login_page import LoginPage

    login = LoginPage(page)
    login.open()
    login.sign_in(STANDARD_USER, STANDARD_PASS)

    inventory = InventoryPage(page)
    inventory.wait_until_loaded()
    return inventory


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot and the page URL whenever a test fails.

    A failure message says what was expected; a screenshot says what was on
    screen. Together they are enough to raise a bug without asking anyone to
    reproduce it first.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if not page:
        return

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", item.name)[:70]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    try:
        shot = EVIDENCE / f"{name}_{stamp}.png"
        page.screenshot(path=str(shot), full_page=True)
        print(f"\n[evidence] screenshot: {shot}")
        print(f"[evidence] page was at: {page.url}")
    except Exception as exc:
        print(f"\n[evidence] could not capture the screen: {exc}")
