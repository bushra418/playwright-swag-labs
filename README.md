# Playwright test suite for Swag Labs

A small end to end suite against [saucedemo.com](https://www.saucedemo.com/). I wrote
it to show how I structure automation, not to cover a demo shop exhaustively.
16 tests, about 20 seconds, running in CI on every push and once a night.

```bash
pip install -r requirements.txt
playwright install chromium
pytest              # headed
HEADLESS=1 pytest   # the way CI runs it
```

## What it covers

| Area | Checks |
|---|---|
| Sign in | Valid credentials, four invalid combinations, and the locked out account |
| Cart | The badge tracks additions and removals. The cart holds what was chosen |
| Checkout | Each detail field enforced on its own. The order total adds up |
| Sorting | By price and by name, both directions |

## Why the code looks the way it does

These are the choices I would defend in a review. The reasons matter more than the code.

### Locators use what the user sees

`get_by_placeholder("Username")` and `get_by_role("button", name="Login")` rather
than `.btn_action`. A CSS class describes how the page is styled today, so it
changes the moment somebody restyles it. The word on the button only changes when
the product changes. Tests that break on a stylesheet edit get ignored, and an
ignored suite is worse than no suite at all.

### Prices are compared as numbers

Sorted as text, `$100.00` comes before `$9.99`, because 1 comes before 9. A string
comparison would report a correctly sorted page as broken and send somebody off to
spend an afternoon proving the application right. The name sort is compared in
lower case for the same reason. Python puts every capital letter before every
small one, which is not what a reader expects.

### Required fields are tested one at a time

Submitting a blank form only proves that something is required. Leaving out the
first name, then the last name, then the postcode is what shows each one is
enforced separately.

### Negative cases check two things

A rejected sign in must not let the user through, and it must say why. A page that
quietly stays put leaves the user guessing. A page that shows an error and signs
them in anyway is worse than either. Checking only one of the two would pass
against both faults.

### Failures leave evidence

Any failing test saves a full page screenshot and prints the URL the browser was
on. The assertion message says what was expected. The screenshot says what was
actually there. Together they are enough to raise a bug without asking anyone to
reproduce it first. CI keeps them as artefacts.

### Credentials come from the environment

These are public demo credentials so nothing is at risk either way. I still keep
them out of the source, because hardcoding them teaches a habit that matters when
the same structure points at a real application.

## A bug in this suite, and the two fixes that were wrong

One test kept failing in CI while passing on my machine. It took three attempts,
and the first two were wrong in a way worth writing down.

It first failed with a timeout on an element. That looked like a bad locator, but
the code was counting cart rows while the browser was still moving from the
product list. So I made `open_cart()` wait for the cart URL, the suite went green
locally, and I thought that was that.

CI disagreed. Second attempt: stop counting rows and then indexing into them, and
read the names in one call instead, so a navigation has no gap to slip through.
Green locally again. CI failed again, and this time the assertion was much more
useful than a timeout had been:

```
Added ['Sauce Labs Backpack', 'Sauce Labs Bolt T-Shirt']
but the cart holds ['Sauce Labs Backpack', 'Sauce Labs Bike Light',
                    'Sauce Labs Bolt T-Shirt', 'Sauce Labs Fleece Jacket',
                    'Sauce Labs Onesie', 'Test.allTheThings() T-Shirt (Red)']
```

Six products. It had read the product list and called it the cart.

The real cause was the locator. I had used `[data-test='inventory-item']` for cart
rows, and the product list uses the same attribute. A locator that matches on both
pages cannot tell which one it is looking at. Worse, `wait_for_url` returns as
soon as the address changes, which is before the new page replaces the old one. I
checked, and at that moment the browser reports `cart.html` while still holding
six product rows and no cart rows at all.

So the code was reading a page that looked entirely valid and was simply the wrong
one. The fix was `.cart_item`, which exists only on the cart. An early read now
finds nothing and waits, instead of finding six things and lying.

What I took from it. A locator should be specific to the page it belongs to,
because ambiguity turns a timing problem into wrong data, and wrong data does not
announce itself. Passing locally is not evidence of passing. And a green suite
after a fix only means the fix was enough that time, which is not the same as
being right.

## Layout

```
pages/      One class per screen. Locators and actions only, no assertions,
            so each test decides for itself what correct means.
tests/      Grouped by what they exercise rather than by page.
config.py   Test accounts, read from the environment.
conftest.py Fixtures and the failure evidence hook.
```

The `signed_in` fixture puts a test on the product list already logged in. Most
tests are about something other than signing in. Repeating the login in each of
them would mean a change to the login screen breaks the whole suite instead of the
one test that covers it.

## What I left out on purpose

No retries and no fixed waits. A retry hides a race instead of fixing it. A sleep
is a guess that is either too short on a slow day or wasted on every other run.
Where something needs waiting for, it waits for that thing.

---

Written by Bushra Jamil. My day job is a much larger Playwright suite against a
government records system. This repository exists because that one belongs to my
employer and is not mine to share.
