from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
import pytest

if TYPE_CHECKING:
    from test.black_box.fynca.canvas_page import CanvasPage

logger = logging.getLogger(__name__)

_ACADEMY_THESIS_STEPS = (
    "1. Start with a ticker",
    "2. Add a chart",
    "3. Add fundamentals",
    "4. Add technicals",
    "5. Auto-arrange",
    "6. Ask AI with context",
)

_ACADEMY_TOPICS = (
    "Technical",
    "Risk",
    "Strategies",
    "Psychology",
    "Options",
    "Advanced",
    "Fundamental",
    "Economic",
)


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-001")
@allure.title("Starter picker exposes Ask Margo, Show Nico, and Just build CTAs")
def test_starter_cta_labels_are_visible(canvas: CanvasPage) -> None:
    if not canvas.is_starter_visible():
        pytest.skip("Starter picker already dismissed on this canvas")

    assert canvas.is_text_visible("Ask Margo")
    assert canvas.is_text_visible("Tell Nico") or canvas.is_text_visible("Show Nico")
    assert canvas.is_text_visible("Start with Otto") or canvas.is_text_visible(
        "Just build"
    )


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-FLOW-002")
@allure.title("Academy opens Getting Started thesis curriculum")
def test_academy_shows_first_thesis_curriculum(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Academy")
    assert canvas.is_heading_visible("Learn Fynca by building your first thesis")
    assert canvas.is_heading_visible("Build your first market thesis")
    for step in _ACADEMY_THESIS_STEPS:
        assert canvas.has_text(step), f"Missing academy step: {step}"


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-003")
@allure.title("Academy lists research topic tracks")
def test_academy_lists_topic_tracks(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    missing = [topic for topic in _ACADEMY_TOPICS if not canvas.has_text(topic)]
    assert not missing, f"Missing academy topics: {missing}"


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-004")
@allure.title("Academy exposes advanced lesson modules from curriculum")
def test_academy_exposes_advanced_lesson_modules(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_academy()

    assert canvas.is_heading_visible("Move faster on the canvas")
    assert canvas.is_heading_visible("Ask AI with your full canvas context")
    assert canvas.is_heading_visible("Build a technical setup")
    assert canvas.is_heading_visible("Research the business")


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-FLOW-005")
@allure.title("Agents opens Bob and Charlie chat with Build and Ask")
def test_agents_opens_bob_and_charlie_chat(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.dismiss_overlays()
    canvas.open_agents()

    assert canvas.is_heading_visible("Bob & Charlie")
    assert canvas.is_chat_visible(), "Message input was not visible in Agents"
    assert canvas.is_tab_visible("Build")
    assert canvas.is_tab_visible("Ask")
    assert "credits" in canvas.get_credits_label().lower()


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-006")
@allure.title("Agents Build mode accepts a canvas prompt")
def test_agents_build_mode_accepts_prompt(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.dismiss_overlays()
    canvas.open_agents()

    canvas.select_chat_mode("Build")
    canvas.fill_chat_message("Build me a comprehensive AAPL canvas with fundamentals")

    assert "AAPL" in canvas.get_message_value()


@pytest.mark.canvas
@pytest.mark.smoke
@pytest.mark.xray("FYNCA-FLOW-007")
@allure.title("Ideas opens welcome screen with catalyst theme and stock suggestions")
def test_ideas_shows_welcome_and_suggestions(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.dismiss_overlays()
    canvas.open_ideas()

    assert canvas.is_heading_visible("Welcome back")
    assert canvas.is_button_visible("Find me a catalyst play for the next two weeks")
    assert canvas.is_button_visible("Should I buy NVDA now or wait")
    assert canvas.has_text("CATALYST")
    assert canvas.has_text("THEME")
    assert canvas.has_text("STOCK")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-008")
@allure.title("Watchlist filters switch between asset classes")
def test_watchlist_asset_filters(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_watchlist()

    for asset_class in ("Stocks", "ETFs", "Crypto", "All"):
        canvas.filter_watchlist(asset_class)
        assert canvas.is_tab_visible(asset_class)


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-009")
@allure.title("Portfolio empty state shows add position CTA")
def test_portfolio_empty_state_cta(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.open_portfolio()

    assert canvas.is_text_visible("No positions yet")
    assert canvas.is_button_visible("Add your first position")
    assert canvas.is_button_visible("Drop a portfolio screenshot")


@pytest.mark.canvas
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-FLOW-010")
@allure.title("Canvas toolbar switches between selection and pan modes")
def test_toolbar_selection_and_pan_modes(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()

    canvas.enable_pan_mode()
    canvas.enable_selection_mode()

    assert canvas.is_button_visible("Pan mode")
    assert canvas.is_button_visible("Selection mode")
    assert canvas.is_react_flow_visible()
