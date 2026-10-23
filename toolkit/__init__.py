"""Playwright Automation Toolkit.

Small, reusable helpers built on the Playwright sync API (headless Chromium):

- :mod:`toolkit.scraper`  -- scrape JavaScript-rendered pages into data
- :mod:`toolkit.capture`  -- full-page screenshots and print-to-PDF
- :mod:`toolkit.forms`    -- automated form filling and submission
"""

from .browser import browser_page
from .scraper import Product, parse_products_html, scrape_products
from .capture import full_page_screenshot, save_pdf
from .forms import parse_confirmation, submit_order_form

__all__ = [
    "browser_page",
    "Product",
    "parse_products_html",
    "scrape_products",
    "full_page_screenshot",
    "save_pdf",
    "parse_confirmation",
    "submit_order_form",
]
