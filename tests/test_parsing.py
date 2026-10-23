"""Unit tests for the pure parsing helpers — no browser required.

These run anywhere (even where the Chromium binary is unavailable) and pin
down the extraction logic that the browser tests exercise end to end.
"""

import pytest

from toolkit.forms import parse_confirmation
from toolkit.scraper import parse_price, parse_products_html, parse_rating

RENDERED_HTML = """
<div id="product-list">
  <article class="product-card" data-sku="SKU-001">
    <h3 class="product-name">Wireless Noise-Cancelling Headphones</h3>
    <span class="product-price">$129.99</span>
    <span class="product-rating">★ 4.8</span>
    <span class="product-stock in">In stock</span>
  </article>
  <article class="product-card" data-sku="SKU-003">
    <h3 class="product-name">USB-C Docking Station</h3>
    <span class="product-price">$89.00</span>
    <span class="product-rating">★ 4.4</span>
    <span class="product-stock out">Out of stock</span>
  </article>
</div>
"""


def test_parse_products_html_extracts_all_fields():
    products = parse_products_html(RENDERED_HTML)
    assert len(products) == 2
    first = products[0]
    assert first.name == "Wireless Noise-Cancelling Headphones"
    assert first.price == 129.99
    assert first.rating == 4.8
    assert first.in_stock is True


def test_parse_products_html_marks_out_of_stock():
    products = parse_products_html(RENDERED_HTML)
    assert products[1].name == "USB-C Docking Station"
    assert products[1].in_stock is False


def test_parse_products_html_empty_when_no_cards():
    assert parse_products_html("<html><body><p>nothing here</p></body></html>") == []


@pytest.mark.parametrize(
    "text,expected",
    [("$49.99", 49.99), ("$1,299.00", 1299.00), ("74.5 USD", 74.5)],
)
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_parse_rating():
    assert parse_rating("★ 4.8") == 4.8
    assert parse_rating("Rated 3.5 out of 5") == 3.5


def test_parse_confirmation_extracts_order_and_email():
    result = parse_confirmation(
        "Thank you, Demo Buyer! Order ORD-4321 confirmed. "
        "A receipt was sent to buyer@example.com."
    )
    assert result["order_id"] == "ORD-4321"
    assert result["email"] == "buyer@example.com"


def test_parse_confirmation_handles_missing_fields():
    result = parse_confirmation("Thanks!")
    assert result["order_id"] is None
    assert result["email"] is None
