# Playwright Automation Toolkit

Practical browser automation in Python with **Playwright** (sync API, headless
Chromium): scrape JavaScript-rendered pages that plain HTTP requests can't see,
capture full-page screenshots and PDFs, and fill/submit web forms end to end.

Everything in this demo runs **offline** against local HTML fixtures, so it can
be tried and tested anywhere — the same functions take a real `https://` URL
when pointed at a live site.

## What's inside

| Module | What it does |
| --- | --- |
| `toolkit/browser.py` | One context manager that launches Chromium with container-safe flags and always cleans up |
| `toolkit/scraper.py` | Waits for JS-rendered product cards, then extracts name / price / rating / stock into dataclasses |
| `toolkit/capture.py` | Full-page screenshot (PNG) and print-ready PDF (A4) capture |
| `toolkit/forms.py` | Fills a checkout form (text, email, select, number, checkbox, textarea), submits it, parses the confirmation |

Design note: extraction logic (`parse_products_html`, `parse_confirmation`,
`parse_price`) is pure Python with no browser dependency, so it is unit-tested
separately from the browser integration tests.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium        # downloads the Chromium build (~150 MB)
```

## Usage

All examples run against the bundled fixtures — no network needed:

```bash
python examples/scrape_demo.py     # JS-rendered products -> output/products.json + .csv
python examples/capture_demo.py    # -> output/products.png + output/products.pdf
python examples/form_demo.py       # submits the demo checkout, prints the confirmation
```

In your own code:

```python
from toolkit import browser_page, scrape_products, submit_order_form

with browser_page() as page:
    products = scrape_products(page, "https://your-shop.example/products")
    for p in products:
        print(p.name, p.price, p.in_stock)
```

## Fixtures (offline demo pages)

- `fixtures/products.html` — a store page whose product list is **empty in the
  raw HTML** and rendered by JavaScript 400 ms after load: a plain `requests`
  fetch sees nothing, the browser sees 5 products.
- `fixtures/form.html` — a checkout form whose submission is handled in-page
  and answered with a deterministic order confirmation (`ORD-####`).

## Tests

```bash
pytest
```

- `tests/test_parsing.py` — unit tests for the pure parsing helpers (no browser).
- `tests/test_browser.py` — integration tests driving real headless Chromium
  against the fixtures: scraped data matches the catalogue, screenshot/PDF
  files are created and valid, and a submitted form returns its confirmation.
  These skip cleanly if the Chromium binary is not installed.

## Typical client work this maps to

- Price/stock monitoring of JS-heavy shops and marketplaces
- Lead/catalogue extraction from directories rendered client-side
- Automated QA evidence: scheduled screenshots and PDF snapshots of pages
- Back-office form automation: repetitive submissions, registrations, uploads
