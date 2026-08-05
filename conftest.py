from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from dotenv import load_dotenv

from fynca import Fynca
from models import TestConfig

if TYPE_CHECKING:
    from collections.abc import Generator

    from playwright.sync_api import Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parent
_AUTH_DIR = _ROOT / "auth"
_STORAGE_STATE = _AUTH_DIR / "storage_state.json"

load_dotenv(_ROOT / ".env")

(_ROOT / "reports" / "allure-results").mkdir(parents=True, exist_ok=True)
(_ROOT / "reports" / "playwright").mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    base_url = os.environ.get("FYNCA_BASE_URL", "https://app.fynca.io").rstrip("/")
    email = os.environ.get("FYNCA_EMAIL", "")
    password = os.environ.get("FYNCA_PASSWORD", "")
    canvas_url = os.environ.get(
        "FYNCA_CANVAS_URL",
        f"{base_url}/canvas/19a6606e631640d979a4a2de",
    )
    return TestConfig(
        base_url=base_url,
        email=email,
        password=password,
        canvas_url=canvas_url,
    )


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def storage_state() -> Path:
    if not _STORAGE_STATE.exists():
        raise pytest.UsageError(
            "Missing auth/storage_state.json. "
            "Run once: .\\.venv\\Scripts\\python.exe save_auth.py "
            "and complete sign-in in the opened Chrome window."
        )
    logger.info("Reusing saved login session: %s", _STORAGE_STATE)
    return _STORAGE_STATE


@pytest.fixture
def context(
    browser: Browser,
    browser_context_args: dict,
    storage_state: Path,
) -> Generator[BrowserContext]:
    ctx = browser.new_context(
        **browser_context_args,
        storage_state=str(storage_state),
    )
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page]:
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def fynca(page: Page, test_config: TestConfig) -> Fynca:
    return Fynca(page, test_config.base_url, test_config.canvas_url)


@pytest.fixture
def canvas(fynca: Fynca):
    return fynca.goto_canvas()


@pytest.fixture
def unauthenticated_page(
    browser: Browser,
    browser_context_args: dict,
) -> Generator[Page]:
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def unauthenticated_fynca(
    unauthenticated_page: Page,
    test_config: TestConfig,
) -> Fynca:
    return Fynca(
        unauthenticated_page,
        test_config.base_url,
        test_config.canvas_url,
    )
