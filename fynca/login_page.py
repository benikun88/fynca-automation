from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class LoginPage:
    """Clerk sign-in page for Fynca."""

    def __init__(self, page: Page, base_url: str, *, navigate: bool = True) -> None:
        self._page = page
        self._base_url = base_url
        if navigate:
            self.reload()

    def reload(self) -> None:
        logger.info("Opening login page")
        self._page.goto(f"{self._base_url}/login")
        self._page.get_by_role("heading", name="Welcome").wait_for()

    def fill_identifier(self, identifier: str) -> None:
        logger.info("Filling identifier")
        self._page.locator("#identifier-field").fill(identifier)

    def fill_password(self, password: str) -> None:
        logger.info("Filling password")
        self._page.locator("#password-field").fill(password)

    def continue_sign_in(self) -> None:
        logger.info("Submitting sign-in form")
        self._page.get_by_role("button", name="Continue", exact=True).click()

    def continue_with_google(self) -> None:
        logger.info("Starting Google sign-in")
        self._dismiss_cookie_banner()
        self._page.get_by_role(
            "button", name=re.compile(r"Google", re.IGNORECASE)
        ).click()

    def wait_until_signed_in(self) -> None:
        logger.info("Waiting until signed in")
        self._page.wait_for_url(lambda url: "/login" not in url)

    def is_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Welcome").is_visible()

    def is_identifier_visible(self) -> bool:
        return self._page.locator("#identifier-field").is_visible()

    def is_google_sign_in_visible(self) -> bool:
        return self._page.get_by_role(
            "button", name=re.compile(r"Google", re.IGNORECASE)
        ).is_visible()

    def is_password_visible(self) -> bool:
        return self._page.locator("#password-field").is_visible()

    def _dismiss_cookie_banner(self) -> None:
        accept = self._page.get_by_role(
            "button",
            name=re.compile(r"Accept|Allow all|Agree|Consent", re.IGNORECASE),
        )
        if accept.is_visible():
            accept.click()
