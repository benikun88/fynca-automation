from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
import pytest

if TYPE_CHECKING:
    from test.black_box.fynca.canvas_page import CanvasPage

logger = logging.getLogger(__name__)


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-CANVAS-001")
@allure.title("Authenticated canvas loads")
def test_canvas_loads_when_authenticated(canvas: CanvasPage) -> None:
    assert "/canvas/" in canvas.get_url(), (
        f"Expected canvas URL, got {canvas.get_url()}"
    )
    assert canvas.is_share_visible(), "Share canvas control was not visible"
    assert canvas.is_react_flow_visible(), "React Flow canvas wrapper was not visible"
    assert canvas.is_button_visible("Toolkit"), (
        "Toolkit sidebar control was not visible"
    )


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-002")
@allure.title("Starter picker offers Margo, Nico, and Otto")
def test_starter_picker_options_are_visible(canvas: CanvasPage) -> None:
    if not canvas.is_starter_visible():
        pytest.skip("Starter picker already dismissed on this canvas")

    assert canvas.is_button_visible("Start from an idea with Margo")
    assert canvas.is_button_visible("Start from what you own with Nico")
    assert canvas.is_button_visible("Start from scratch with Otto")


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-CANVAS-003")
@allure.title("Start from scratch dismisses starter picker")
def test_start_from_scratch_dismisses_picker(canvas: CanvasPage) -> None:
    if not canvas.is_starter_visible():
        pytest.skip("Starter picker already dismissed on this canvas")

    canvas.start_from_scratch()

    assert not canvas.is_starter_visible(), "Starter picker remained visible after Otto"


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-004")
@allure.title("Watchlist panel opens with asset filters")
def test_open_watchlist_panel(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_watchlist()

    assert canvas.is_heading_visible("Watchlist")
    assert canvas.is_tab_visible("Stocks")
    assert canvas.is_text_visible("Your watchlist is empty")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-005")
@allure.title("Portfolio panel opens with empty state")
def test_open_portfolio_panel(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_portfolio()

    assert canvas.is_heading_visible("Portfolio")
    assert canvas.is_text_visible("No positions yet")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-006")
@allure.title("Canvases panel opens")
def test_open_canvases_panel(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_canvases()

    assert canvas.is_heading_visible("Canvases")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-007")
@allure.title("Templates panel opens")
def test_open_templates_panel(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_templates()

    assert canvas.is_heading_visible("Templates")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-008")
@allure.title("Academy education center opens")
def test_open_academy_education_center(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-009")
@allure.title("Canvas zoom and fit controls work")
def test_canvas_zoom_controls(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()

    canvas.zoom_in()
    canvas.fit_to_page()
    canvas.zoom_out()

    assert canvas.is_react_flow_visible(), "Canvas disappeared after zoom controls"


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-010")
@allure.title("Bob and Charlie chat supports Build and Ask modes")
def test_chat_build_and_ask_modes(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.dismiss_overlays()
    canvas.open_agents()

    if not canvas.is_chat_visible():
        pytest.skip("Bob & Charlie chat panel is closed on this canvas")

    canvas.select_chat_mode("Ask")
    canvas.fill_chat_message("Summarize this canvas")
    canvas.select_chat_mode("Build")
    canvas.fill_chat_message("Build me a technical overview")

    assert canvas.get_message_value() == "Build me a technical overview"
    assert "credits" in canvas.get_credits_label().lower()


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-CANVAS-011")
@allure.title("Share canvas opens dialog")
def test_share_canvas_control(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()

    canvas.share()

    assert canvas.is_share_dialog_visible(), "Share dialog was not visible"
