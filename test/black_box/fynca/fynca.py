from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from test.black_box.fynca.canvas_page import CanvasPage
from test.black_box.fynca.home_page import HomePage
from test.black_box.fynca.login_page import LoginPage

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class Fynca:
    """Facade for navigating Fynca app pages."""

    def __init__(self, page: Page, base_url: str, canvas_url: str) -> None:
        self._page = page
        self._base_url = base_url
        self._canvas_url = canvas_url

    def goto_login(self) -> LoginPage:
        logger.info("Navigating to login")
        return LoginPage(self._page, self._base_url)

    def goto_home(self) -> HomePage:
        logger.info("Navigating to home")
        return HomePage(self._page, self._base_url)

    def goto_canvas(self) -> CanvasPage:
        logger.info("Navigating to canvas")
        return CanvasPage(self._page, self._base_url, self._canvas_url)
