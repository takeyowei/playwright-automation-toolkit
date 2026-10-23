"""Demo: full-page screenshot + PDF capture of the demo store page.

Run from the project root:

    python examples/capture_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from toolkit import browser_page, full_page_screenshot, save_pdf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "fixtures" / "products.html").as_uri()
OUT_DIR = ROOT / "output"


def main() -> None:
    with browser_page() as page:
        png = full_page_screenshot(page, URL, OUT_DIR / "products.png")
        pdf = save_pdf(page, URL, OUT_DIR / "products.pdf")
    print(f"screenshot: {png} ({png.stat().st_size} bytes)")
    print(f"pdf:        {pdf} ({pdf.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
