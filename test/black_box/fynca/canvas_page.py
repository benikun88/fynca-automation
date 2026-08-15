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
        self._wait_for_canvas_or_login()
        self.dismiss_promo()
        share = self._page.get_by_role("button", name="Share canvas")
        if not share.is_visible():
            logger.info("Share control not ready — reloading canvas once")
            self._page.reload(wait_until="domcontentloaded")
            self._wait_for_canvas_or_login()
            self.dismiss_promo()
        self._page.get_by_role("button", name="Share canvas").wait_for()
        self._page.get_by_role("button", name="Toolkit").wait_for()
        self._page.get_by_test_id("rf__wrapper").wait_for()

    def _wait_for_canvas_or_login(self) -> None:
        share = self._page.get_by_role("button", name="Share canvas")
        login = self._page.get_by_role("heading", name="Welcome")
        promo_close = self._page.get_by_role("button", name="Close announcement")
        starter = self._starter_heading()
        share.or_(login).or_(promo_close).or_(starter).wait_for()
        self._raise_if_session_expired()

    def _starter_heading(self) -> Locator:
        return self._page.get_by_role(
            "heading", name="Pick your starting point"
        ).or_(
            self._page.get_by_role("heading", name="What are you starting with?")
        )

    def dismiss_promo(self) -> None:
        close = self._page.get_by_role("button", name="Close announcement")
        if not close.is_visible():
            return
        logger.info("Dismissing promo announcement")
        close.click()
        close.wait_for(state="hidden")

    def _raise_if_session_expired(self) -> None:
        on_login_url = "/login" in self._page.url
        login_visible = self._page.get_by_role("heading", name="Welcome").is_visible()
        if not on_login_url and not login_visible:
            return
        raise RuntimeError(
            "Saved Clerk session expired or was rejected; landed on login. "
            "Run save_auth.py locally, then update GitHub secret FYNCA_STORAGE_STATE_B64. "
            f"Current URL: {self._page.url}"
        )

    def get_url(self) -> str:
        return self._page.url

    def is_share_visible(self) -> bool:
        return self._page.get_by_role("button", name="Share canvas").is_visible()

    def is_starter_visible(self) -> bool:
        return self._starter_heading().is_visible()

    def start_from_scratch(self) -> None:
        logger.info("Starting canvas from scratch with Otto")
        self._page.get_by_role("button", name="Start from scratch with Otto").or_(
            self._page.get_by_role("button", name="Start with Otto")
        ).click()
        self._starter_heading().wait_for(state="hidden")

    def start_from_idea(self) -> None:
        logger.info("Starting canvas from an idea with Margo")
        self._page.get_by_role("button", name="Start from an idea with Margo").or_(
            self._page.get_by_role("button", name="Ask Margo")
        ).click()

    def start_from_holdings(self) -> None:
        logger.info("Starting canvas from holdings with Nico")
        self._page.get_by_role(
            "button", name="Start from what you own with Nico"
        ).or_(self._page.get_by_role("button", name="Tell Nico")).click()

    def ensure_workspace_ready(self) -> None:
        if self.is_starter_visible():
            self.start_from_scratch()

    def open_watchlist(self) -> None:
        logger.info("Opening Watchlist")
        self._sidebar("Watchlist").click()
        self._page.get_by_role("heading", name="Watchlist").wait_for()

    def filter_watchlist(self, asset_class: str) -> None:
        logger.info("Filtering watchlist by %s", asset_class)
        self._page.get_by_role("tab", name=asset_class, exact=True).click()

    def open_portfolio(self) -> None:
        logger.info("Opening Portfolio")
        self._sidebar("Portfolio").click()
        self._page.get_by_text("No positions yet", exact=True).first.wait_for()

    def filter_portfolio(self, asset_class: str) -> None:
        logger.info("Filtering portfolio by %s", asset_class)
        self._page.get_by_role("tab", name=asset_class, exact=True).click()

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

    def open_agents(self) -> None:
        logger.info("Opening Agents (Bob & Charlie)")
        self._sidebar("Agents").click()
        self._page.get_by_role("heading", name="Bob & Charlie").wait_for()
        self._page.get_by_role("textbox", name="Message input").wait_for()
        self._chat_mode_control("Build").first.wait_for()

    def open_ideas(self) -> None:
        logger.info("Opening Ideas")
        self._sidebar("Ideas").click()
        self._page.get_by_role("heading", name="Welcome back").wait_for()

    def open_toolkit(self) -> None:
        logger.info("Opening Toolkit")
        self._sidebar("Toolkit").click()
        self._page.get_by_role("heading", name="Toolkit").wait_for()

    def select_academy_lesson(self, title: str) -> None:
        logger.info("Selecting academy lesson: %s", title)
        self._page.get_by_text(title, exact=False).first.click()

    def enable_pan_mode(self) -> None:
        logger.info("Enabling pan mode")
        self._page.get_by_role("button", name="Pan mode").click()

    def enable_selection_mode(self) -> None:
        logger.info("Enabling selection mode")
        self._page.get_by_role("button", name="Selection mode").click()

    def share(self) -> None:
        logger.info("Opening share canvas")
        self._page.get_by_role("button", name="Share canvas").click()

    def is_share_dialog_visible(self) -> bool:
        dialog = self._page.get_by_role("dialog")
        return dialog.count() > 0 and dialog.first.is_visible()

    def dismiss_overlays(self) -> None:
        logger.info("Dismissing overlays")
        self.dismiss_promo()
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
        control = self._chat_mode_control(mode).first
        control.wait_for()
        control.scroll_into_view_if_needed()
        try:
            control.click()
        except Exception:
            logger.info("Chat mode %s click intercepted; retrying with force", mode)
            control.click(force=True)

    def _chat_mode_control(self, mode: str) -> Locator:
        return (
            self._page.get_by_role("radio", name=mode, exact=True)
            .or_(self._page.get_by_role("tab", name=mode, exact=True))
            .or_(self._page.get_by_role("button", name=mode, exact=True))
            .or_(self._page.locator(f'button[data-mode="{mode.lower()}"]'))
        )

    def is_tab_visible(self, name: str) -> bool:
        control = (
            self._page.get_by_role("radio", name=name, exact=True)
            .or_(self._page.get_by_role("tab", name=name, exact=True))
            .or_(self._page.get_by_role("button", name=name, exact=True))
        )
        if control.count() == 0:
            return False
        try:
            control.first.scroll_into_view_if_needed(timeout=5_000)
        except Exception:
            pass
        return control.first.is_visible()

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
        return self._page.get_by_text(text, exact=True).first.is_visible()

    def has_text(self, text: str) -> bool:
        return self._page.get_by_text(text, exact=False).first.is_visible()

    def is_button_visible(self, name: str) -> bool:
        locator = self._page.get_by_role("button", name=name)
        return locator.count() > 0 and locator.first.is_visible()

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
