"""Scraping helpers for JavaScript-rendered pages.

The split is deliberate:

- ``scrape_products`` drives a real browser: it waits until the page's
  JavaScript has rendered the product cards, then grabs the live DOM.
- ``parse_products_html`` is a pure function (HTML string -> data) built on
  the standard library only, so the extraction logic can be unit-tested
  without launching a browser at all.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser

from playwright.sync_api import Page

CARD_CLASS = "product-card"
FIELD_CLASSES = ("product-name", "product-price", "product-rating", "product-stock")


@dataclass
class Product:
    name: str
    price: float
    rating: float
    in_stock: bool

    def to_dict(self) -> dict:
        return asdict(self)


class _ProductCardParser(HTMLParser):
    """Collects product-card fields from rendered HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.products: list[dict] = []
        self._card: dict | None = None
        self._card_depth = 0
        self._field: str | None = None
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = (dict(attrs).get("class") or "").split()
        if self._card is None and CARD_CLASS in classes:
            self._card = {}
            self._card_depth = 1
            return
        if self._card is not None:
            self._card_depth += 1
            for field in FIELD_CLASSES:
                if field in classes:
                    self._field = field
                    self._chunks = []

    def handle_endtag(self, tag: str) -> None:
        if self._card is None:
            return
        if self._field is not None:
            self._card[self._field] = "".join(self._chunks).strip()
            self._field = None
        self._card_depth -= 1
        if self._card_depth == 0:
            self.products.append(self._card)
            self._card = None

    def handle_data(self, data: str) -> None:
        if self._field is not None:
            self._chunks.append(data)


_PRICE_RE = re.compile(r"[\d,]+(?:\.\d+)?")
_RATING_RE = re.compile(r"\d+(?:\.\d+)?")


def parse_price(text: str) -> float:
    """``"$1,299.99"`` -> ``1299.99``."""
    match = _PRICE_RE.search(text.replace(" ", ""))
    if not match:
        raise ValueError(f"no price found in {text!r}")
    return float(match.group(0).replace(",", ""))


def parse_rating(text: str) -> float:
    """``"★ 4.8"`` -> ``4.8``."""
    match = _RATING_RE.search(text)
    if not match:
        raise ValueError(f"no rating found in {text!r}")
    return float(match.group(0))


def parse_products_html(html: str) -> list[Product]:
    """Turn rendered product-list HTML into a list of :class:`Product`."""
    parser = _ProductCardParser()
    parser.feed(html)
    products = []
    for raw in parser.products:
        products.append(
            Product(
                name=raw.get("product-name", ""),
                price=parse_price(raw.get("product-price", "")),
                rating=parse_rating(raw.get("product-rating", "")),
                in_stock="out" not in raw.get("product-stock", "").lower(),
            )
        )
    return products


def scrape_products(
    page: Page,
    url: str,
    *,
    wait_selector: str = ".product-card",
    timeout_ms: int = 10_000,
) -> list[Product]:
    """Open ``url``, wait for JS-rendered cards, return them as products."""
    page.goto(url)
    # The whole point of using a browser: wait until client-side rendering
    # has actually produced the cards before reading the DOM.
    page.wait_for_selector(wait_selector, timeout=timeout_ms)
    return parse_products_html(page.content())
