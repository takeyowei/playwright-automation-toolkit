"""Page capture helpers: full-page screenshots and print-to-PDF.

Useful for visual QA snapshots, archiving pages for clients, generating
PDF copies of invoices/reports, and before/after evidence in audits.
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page


def full_page_screenshot(page: Page, url: str, out_path: str | Path) -> Path:
    """Screenshot the *entire* page (not just the viewport) to ``out_path``."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(out), full_page=True)
    return out


def save_pdf(page: Page, url: str, out_path: str | Path) -> Path:
    """Render ``url`` to a print-ready A4 PDF at ``out_path`` (Chromium only)."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.pdf(path=str(out), format="A4", print_background=True)
    return out
