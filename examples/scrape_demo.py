"""Demo: scrape the JavaScript-rendered demo store into JSON + CSV.

Run from the project root:

    python examples/scrape_demo.py

Swap ``URL`` for any real JS-heavy listing page whose card markup matches
(or adapt the class names in ``toolkit/scraper.py``).
"""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from toolkit import browser_page, scrape_products  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "fixtures" / "products.html").as_uri()
OUT_DIR = ROOT / "output"


def main() -> None:
    with browser_page() as page:
        products = scrape_products(page, URL)

    OUT_DIR.mkdir(exist_ok=True)
    rows = [p.to_dict() for p in products]
    (OUT_DIR / "products.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with (OUT_DIR / "products.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "price", "rating", "in_stock"])
        writer.writeheader()
        writer.writerows(rows)

    for p in products:
        stock = "in stock" if p.in_stock else "OUT of stock"
        print(f"{p.name:<42} ${p.price:>7.2f}  ★{p.rating}  {stock}")
    print(f"\n{len(products)} products -> output/products.json, output/products.csv")


if __name__ == "__main__":
    main()
