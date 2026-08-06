from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class HomePage:
    """Authenticated Fynca app shell after login."""

    def __init__(self, page: Page, base_url: str, *, navigate: bool = True) -> None:
        self._page = page
        self._base_url = base_url
        if navigate:
            self.reload()

    def reload(self) -> None:
        logger.info("Opening home page")
        self._page.goto(f"{self._base_url}/")
        self._page.wait_for_url(lambda url: "/login" not in url)
        self._page.locator("body").wait_for(state="visible")

    def get_url(self) -> str:
        return self._page.url

    def is_authenticated(self) -> bool:
        return "/login" not in self._page.url
