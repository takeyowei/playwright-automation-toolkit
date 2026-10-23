"""Demo: fill and submit the demo checkout form end to end.

Run from the project root:

    python examples/form_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from toolkit import browser_page, submit_order_form  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
URL = (ROOT / "fixtures" / "form.html").as_uri()


def main() -> None:
    with browser_page() as page:
        result = submit_order_form(
            page,
            URL,
            name="Demo Buyer",
            email="buyer@example.com",
            plan="premium",
            quantity=2,
            subscribe=True,
            notes="Please gift-wrap.",
        )
    print("Form submitted. Confirmation:")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
