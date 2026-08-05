from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import allure
import pytest

if TYPE_CHECKING:
    from fynca.canvas_page import CanvasPage

logger = logging.getLogger(__name__)

_REQUIRED_CONTROLS = (
    "Share canvas",
    "Create new canvas",
    "Watchlist",
    "Portfolio",
    "Canvases",
    "Templates",
    "Academy",
    "Fit to page",
    "Zoom in",
    "Zoom out",
)


@pytest.mark.exploratory
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-EXPLORE-001")
@allure.title("Exploratory locator sweep finds required canvas controls")
def test_exploratory_required_locators(canvas: CanvasPage) -> None:
    missing = [
        name for name in _REQUIRED_CONTROLS if not canvas.is_button_visible(name)
    ]

    assert not missing, f"Missing required controls: {missing}"


@pytest.mark.exploratory
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-EXPLORE-002")
@allure.title("Exploratory sidebar discovery returns known panels")
def test_exploratory_sidebar_discovery(canvas: CanvasPage) -> None:
    names = canvas.sidebar_names()

    assert "Watchlist" in names
    assert "Portfolio" in names
    assert "Canvases" in names
    assert len(names) >= 8, f"Expected at least 8 sidebar items, got {names}"
