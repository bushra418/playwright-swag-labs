# Playwright test suite — Swag Labs

A small end-to-end suite against [saucedemo.com](https://www.saucedemo.com/), written
to show how I structure automation rather than to cover a demo shop exhaustively.
16 tests, about 20 seconds, running in CI on every push and nightly.

```bash
pip install -r requirements.txt
playwright install chromium
pytest              # headed
HEADLESS=1 pytest   # as CI runs it
```

## What it covers

| Area | Checks |
|---|---|
| Sign in | Valid credentials, four invalid combinations, and the locked-out account |
| Cart | The badge tracks additions *and* removals; the cart holds what was chosen |
| Checkout | Each detail field enforced individually; the order total adds up |
| Sorting | By price and by name, both directions |

## Decisions worth explaining

These are the choices I would defend in review, and the reasons matter more than
the code.

**Locators describe what the user sees.** `get_by_placeholder("Username")` and
`get_by_role("button", name="Login")` rather than `.btn_action`. A CSS class
describes how a page is styled today and changes when someone restyles it; the
word on the button changes only when the product changes. Tests that break on a
stylesheet edit get ignored, and an ignored suite is worse than no suite.

**Prices are compared as numbers.** Sorted as text, `$100.00` comes before
`$9.99`, because `1` precedes `9`. A string comparison would report a correctly
sorted page as broken and send someone off to prove the application right. The
same reasoning applies to the name sort, which is compared case-insensitively —
Python puts every capital before every lower-case letter, which no user expects.

**Required fields are tested one at a time.** Submitting a blank form proves only
that *something* is required. Leaving out the first name, then the last name,
then the postcode is what shows each is enforced separately.

**Negative cases assert two things.** A rejected sign-in must not let the user
through *and* must say why. A page that silently stays put leaves the user
guessing; a page that shows an error while signing them in anyway is worse than
either. Checking only one of the two would pass against both faults.

**Failures leave evidence.** Any failing test saves a full-page screenshot and
prints the URL the browser was on. A message says what was expected; the
screenshot says what was actually there — together they are enough to raise a
bug without asking anyone to reproduce it first. CI keeps them as artefacts.

**Credentials come from the environment.** They are public demo credentials, so
nothing is at risk either way — but hardcoding them teaches a habit that matters
when the same structure points at a real application.

## A bug this suite found in itself

The first run failed on one test with a timeout on an element, which looked like
a locator problem. It wasn't. `count()` was being read while the browser was
still navigating from the product list to the cart — six rows on screen, then
two by the time the third was requested.

The fix was for `open_cart()` to wait for the cart URL before returning, so the
page object never hands back a half-navigated page. The interesting part is that
the error message blamed an element when the cause was a navigation, which is
why the wait belongs in the page object rather than in each test that trips over
it.

## Layout

```
pages/      One class per screen. Locators and actions only — no assertions,
            so each test decides for itself what correct means.
tests/      Grouped by what they exercise, not by page.
conftest.py Fixtures, and the failure-evidence hook.
```

The `signed_in` fixture lands a test on the product list already authenticated.
Most tests are about something other than signing in, and repeating the login in
each would mean a change to the login screen breaking every test in the suite
rather than the one that covers it.

## What I have left out, deliberately

No retries and no waits for fixed durations. A retry hides a race rather than
fixing it, and a `sleep` is a guess that is either too short on a slow day or
wasted on every other run. Where something needs waiting for, it waits for the
thing itself.

---

Built by Bushra Jamil. My day job is a considerably larger Playwright suite
against a government records system — this repository exists because that one
is not mine to share.
