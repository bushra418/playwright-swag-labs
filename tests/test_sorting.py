import pytest


@pytest.mark.parametrize(
    "option, ascending",
    [
        ("Price (low to high)", True),
        ("Price (high to low)", False),
    ],
)
def test_products_sort_by_price(signed_in, option, ascending):
    """Sorting by price orders the products by their value.

    The prices are compared as numbers, not as the text on screen. Sorted as
    text, "$100.00" comes before "$9.99" because 1 comes before 9. A string
    comparison would report a correctly sorted page as broken, and the tester
    would spend an afternoon proving the application right.
    """
    signed_in.sort_by(option)
    prices = signed_in.prices()
    assert len(prices) > 1, "Need more than one product to test sorting"

    expected = sorted(prices, reverse=not ascending)
    assert prices == expected, (
        f"Sorting by {option!r} produced {prices}, which is not in "
        f"{'ascending' if ascending else 'descending'} order"
    )


@pytest.mark.parametrize(
    "option, reverse",
    [
        ("Name (A to Z)", False),
        ("Name (Z to A)", True),
    ],
)
def test_products_sort_by_name(signed_in, option, reverse):
    """Sorting by name is case-insensitive, as a reader would expect.

    Compared in lower case deliberately: Python sorts every capital letter
    before every lower-case one, so a list a person would call correctly sorted
    fails a naive comparison.
    """
    signed_in.sort_by(option)
    names = signed_in.product_names()
    assert len(names) > 1, "Need more than one product to test sorting"

    expected = sorted(names, key=str.lower, reverse=reverse)
    assert names == expected, (
        f"Sorting by {option!r} produced {names}, which is not the expected order"
    )
