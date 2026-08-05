from __future__ import annotations

"""One-time headed login that saves Playwright storage state for later tests.

Google blocks automated Chromium for OAuth ("This browser or app may not be
secure"). Run this script once in real Chrome, complete Google sign-in yourself,
then tests reuse auth/storage_state.json.

Usage:
    .\\.venv\\Scripts\\python.exe save_auth.py
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from fynca.login_page import LoginPage

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parent
_AUTH_DIR = _ROOT / "auth"
_STORAGE_STATE = _AUTH_DIR / "storage_state.json"
_LOGIN_TIMEOUT_MS = 300_000

load_dotenv(_ROOT / ".env")


def main() -> int:
    base_url = os.environ.get("FYNCA_BASE_URL", "https://app.fynca.io").rstrip("/")
    _AUTH_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Opening real Chrome (headed) for Fynca login")
    logger.info(
        "Sign in manually (Google or email). Session saves when you leave /login."
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        try:
            LoginPage(page, base_url)
            logger.info(
                "Waiting for successful login (up to %ss)...",
                _LOGIN_TIMEOUT_MS // 1000,
            )
            page.wait_for_url(
                lambda url: base_url in url and "/login" not in url,
                timeout=_LOGIN_TIMEOUT_MS,
            )

            context.storage_state(path=str(_STORAGE_STATE))
            logger.info("Saved login session to %s", _STORAGE_STATE)
        except Exception:
            logger.exception("Login session was not saved")
            return 1
        finally:
            context.close()
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
