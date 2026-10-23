"""Integration tests: real headless Chromium against the local fixtures.

If the Chromium binary is not installed (``playwright install chromium``
has not been run), every test here skips with an explanation instead of
failing — the pure-logic tests in ``test_parsing.py`` still cover the
extraction code.
"""

import re

import pytest

from conftest import FORM_URL, PRODUCTS_URL
from toolkit import (
    browser_page,
    full_page_screenshot,
    save_pdf,
    scrape_products,
    submit_order_form,
)

EXPECTED_PRODUCTS = [
    ("Wireless Noise-Cancelling Headphones", 129.99, 4.8, True),
    ("Mechanical Keyboard K87", 74.50, 4.6, True),
    ("USB-C Docking Station", 89.00, 4.4, False),
    ("Ergonomic Wireless Mouse", 45.99, 4.7, True),
    ("4K USB Webcam", 119.00, 4.5, True),
]


@pytest.fixture()
def page():
    try:
        with browser_page() as pw_page:
            yield pw_page
    except Exception as exc:  # browser binary missing / cannot launch
        pytest.skip(f"Chromium unavailable, skipping browser test: {exc}")


def test_scrape_js_rendered_products(page):
    products = scrape_products(page, PRODUCTS_URL)
    got = [(p.name, p.price, p.rating, p.in_stock) for p in products]
    assert got == EXPECTED_PRODUCTS


def test_raw_html_has_no_products_without_js(page):
    """Proves the fixture really needs a browser: cards exist only after JS runs."""
    page.goto(PRODUCTS_URL)
    early_html = page.content()
    # Immediately after load the container is still empty (JS renders at 400ms).
    assert 'id="product-list"' in early_html
    page.wait_for_selector(".product-card")
    assert page.locator(".product-card").count() == 5


def test_full_page_screenshot(page, tmp_path):
    out = full_page_screenshot(page, PRODUCTS_URL, tmp_path / "shot.png")
    assert out.exists()
    assert out.stat().st_size > 5_000
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic


def test_save_pdf(page, tmp_path):
    out = save_pdf(page, PRODUCTS_URL, tmp_path / "page.pdf")
    assert out.exists()
    assert out.stat().st_size > 2_000
    assert out.read_bytes()[:4] == b"%PDF"


def test_form_submission_returns_confirmation(page):
    result = submit_order_form(
        page,
        FORM_URL,
        name="Demo Buyer",
        email="buyer@example.com",
        plan="premium",
        quantity=2,
        subscribe=True,
        notes="Please gift-wrap.",
    )
    assert result["order_id"] is not None
    assert re.fullmatch(r"ORD-\d{4}", result["order_id"])
    assert result["email"] == "buyer@example.com"
    assert "Demo Buyer" in result["raw_text"]
    assert "premium" in result["raw_text"]
