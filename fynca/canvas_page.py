from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class CanvasPage:
    """Authenticated Fynca research canvas workspace."""

    def __init__(
        self,
        page: Page,
        base_url: str,
        canvas_url: str,
        *,
        navigate: bool = True,
    ) -> None:
        self._page = page
        self._base_url = base_url
        self._canvas_url = canvas_url
        if navigate:
            self.reload()

    def reload(self) -> None:
        logger.info("Opening canvas: %s", self._canvas_url)
        self._page.goto(self._canvas_url, wait_until="domcontentloaded")
        share = self._page.get_by_role("button", name="Share canvas")
        try:
            share.wait_for()
        except Exception:
            logger.info("Share control not ready — reloading canvas once")
            self._page.reload(wait_until="domcontentloaded")
            share.wait_for()
        self._page.get_by_role("button", name="Toolkit").wait_for()
        self._page.get_by_test_id("rf__wrapper").wait_for()

    def get_url(self) -> str:
        return self._page.url

    def is_share_visible(self) -> bool:
        return self._page.get_by_role("button", name="Share canvas").is_visible()

    def is_starter_visible(self) -> bool:
        return self._page.get_by_role("heading", name="Pick your starting point").is_visible()

    def start_from_scratch(self) -> None:
        logger.info("Starting canvas from scratch with Otto")
        self._page.get_by_role("button", name="Start from scratch with Otto").click()
        self._page.get_by_role("heading", name="Pick your starting point").wait_for(
            state="hidden"
        )

    def ensure_workspace_ready(self) -> None:
        if self.is_starter_visible():
            self.start_from_scratch()

    def open_watchlist(self) -> None:
        logger.info("Opening Watchlist")
        self._sidebar("Watchlist").click()
        self._page.get_by_role("heading", name="Watchlist").wait_for()

    def open_portfolio(self) -> None:
        logger.info("Opening Portfolio")
        self._sidebar("Portfolio").click()
        self._page.get_by_text("No positions yet", exact=True).first.wait_for()

    def open_canvases(self) -> None:
        logger.info("Opening Canvases")
        self._sidebar("Canvases").click()
        self._page.get_by_role("heading", name="Canvases").wait_for()

    def open_templates(self) -> None:
        logger.info("Opening Templates")
        self._sidebar("Templates").click()
        self._page.get_by_role("heading", name="Templates").wait_for()

    def open_academy(self) -> None:
        logger.info("Opening Academy")
        self._sidebar("Academy").click()
        self._page.get_by_role("heading", name="Academy", exact=True).wait_for()

    def open_toolkit(self) -> None:
        logger.info("Opening Toolkit")
        self._sidebar("Toolkit").click()
        self._page.get_by_role("heading", name="Toolkit").wait_for()

    def share(self) -> None:
        logger.info("Opening share canvas")
        self._page.get_by_role("button", name="Share canvas").click()

    def is_share_dialog_visible(self) -> bool:
        dialog = self._page.get_by_role("dialog")
        return dialog.count() > 0 and dialog.first.is_visible()

    def dismiss_overlays(self) -> None:
        logger.info("Dismissing overlays")
        self._page.keyboard.press("Escape")

    def fit_to_page(self) -> None:
        logger.info("Fitting canvas to page")
        self._page.get_by_role("button", name="Fit to page").click()

    def zoom_in(self) -> None:
        logger.info("Zooming in")
        self._page.get_by_role("button", name="Zoom in").click()

    def zoom_out(self) -> None:
        logger.info("Zooming out")
        self._page.get_by_role("button", name="Zoom out").click()

    def is_chat_visible(self) -> bool:
        return self._page.get_by_role("textbox", name="Message input").is_visible()

    def select_chat_mode(self, mode: str) -> None:
        logger.info("Selecting chat mode: %s", mode)
        tab = self._page.get_by_role("tab", name=mode, exact=True)
        button = self._page.get_by_role("button", name=mode, exact=True)
        tab.or_(button).click()

    def fill_chat_message(self, message: str) -> None:
        logger.info("Filling chat message")
        self._page.get_by_role("textbox", name="Message input").fill(message)

    def get_credits_label(self) -> str:
        return self._page.get_by_role("button", name="AI credits").inner_text()

    def get_message_value(self) -> str:
        return self._page.get_by_role("textbox", name="Message input").input_value()

    def is_react_flow_visible(self) -> bool:
        return self._page.get_by_test_id("rf__wrapper").is_visible()

    def is_heading_visible(self, name: str) -> bool:
        return self._page.get_by_role("heading", name=name).is_visible()

    def is_text_visible(self, text: str) -> bool:
        return self._page.get_by_text(text, exact=True).is_visible()

    def is_button_visible(self, name: str) -> bool:
        locator = self._page.get_by_role("button", name=name)
        return locator.count() > 0 and locator.first.is_visible()

    def is_tab_visible(self, name: str) -> bool:
        tab = self._page.get_by_role("tab", name=name, exact=True)
        button = self._page.get_by_role("button", name=name, exact=True)
        return tab.or_(button).is_visible()

    def open_sidebar(self, name: str) -> None:
        logger.info("Opening sidebar: %s", name)
        self._sidebar(name).click()

    def sidebar_names(self) -> list[str]:
        names = [
            "Toolkit",
            "Agents",
            "Ideas",
            "Canvases",
            "Templates",
            "Watchlist",
            "Portfolio",
            "Index",
            "Academy",
            "Themes",
            "Shortcuts",
            "Help",
        ]
        return [name for name in names if self._sidebar(name).is_visible()]

    def _sidebar(self, name: str) -> Locator:
        return self._page.get_by_role("button", name=name)
