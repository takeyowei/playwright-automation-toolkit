"""Browser lifecycle helpers.

One place that knows how to launch headless Chromium with the flags that
make it behave inside containers, CI runners and small VMs.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import Browser, Page, sync_playwright

# Flags that keep Chromium stable in sandboxed/container environments.
LAUNCH_ARGS = ["--no-sandbox", "--disable-dev-shm-usage"]


@contextmanager
def browser_page(
    *,
    headless: bool = True,
    viewport: dict | None = None,
) -> Iterator[Page]:
    """Yield a ready-to-use Playwright page; always clean up afterwards.

    Usage::

        with browser_page() as page:
            page.goto("https://example.com")
    """
    with sync_playwright() as pw:
        browser: Browser = pw.chromium.launch(headless=headless, args=LAUNCH_ARGS)
        context = browser.new_context(viewport=viewport or {"width": 1280, "height": 800})
        page = context.new_page()
        try:
            yield page
        finally:
            context.close()
            browser.close()
