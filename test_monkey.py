from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

import allure
import pytest

if TYPE_CHECKING:
    from fynca.canvas_page import CanvasPage

logger = logging.getLogger(__name__)

_SIDEBAR = (
    "Toolkit",
    "Canvases",
    "Templates",
    "Watchlist",
    "Portfolio",
    "Index",
    "Academy",
    "Themes",
    "Help",
)


@pytest.mark.monkey
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-MONKEY-001")
@allure.title("Monkey clicks random sidebar panels without crashing")
def test_monkey_random_sidebar_clicks(canvas: CanvasPage) -> None:
    canvas.ensure_workspace_ready()
    canvas.dismiss_overlays()

    visible = [name for name in _SIDEBAR if canvas.is_button_visible(name)]
    assert visible, "No sidebar buttons were visible for monkey testing"

    picks = random.sample(visible, k=min(5, len(visible)))
    for name in picks:
        logger.info("Monkey opening sidebar: %s", name)
        canvas.dismiss_overlays()
        canvas.open_sidebar(name)
        assert "/login" not in canvas.get_url(), f"Logged out after opening {name}"
        assert canvas.is_react_flow_visible(), f"Canvas lost after opening {name}"
