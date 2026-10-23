"""Automated form filling and submission.

``submit_order_form`` drives the demo checkout form end to end.
``parse_confirmation`` is a pure helper that pulls the structured result
(order id, name, email) out of the confirmation text, so it can be
unit-tested without a browser.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

_ORDER_ID_RE = re.compile(r"ORD-\d+")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def parse_confirmation(text: str) -> dict:
    """Extract ``{order_id, email}`` from a confirmation message body."""
    order = _ORDER_ID_RE.search(text)
    email = _EMAIL_RE.search(text)
    return {
        "order_id": order.group(0) if order else None,
        "email": email.group(0) if email else None,
        "raw_text": " ".join(text.split()),
    }


def submit_order_form(
    page: Page,
    url: str,
    *,
    name: str,
    email: str,
    plan: str = "standard",
    quantity: int = 1,
    subscribe: bool = False,
    notes: str = "",
    confirmation_selector: str = "#confirmation",
    timeout_ms: int = 10_000,
) -> dict:
    """Fill the demo order form, submit it, return the parsed confirmation."""
    page.goto(url)
    page.fill("#name", name)
    page.fill("#email", email)
    page.select_option("#plan", plan)
    page.fill("#quantity", str(quantity))
    if subscribe:
        page.check("#subscribe")
    if notes:
        page.fill("#notes", notes)
    page.click("button[type=submit]")
    page.wait_for_selector(confirmation_selector, timeout=timeout_ms)
    result = parse_confirmation(page.inner_text(confirmation_selector))
    result["name"] = name
    result["plan"] = plan
    result["quantity"] = quantity
    return result
