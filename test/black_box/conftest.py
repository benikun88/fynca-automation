from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from allure_commons.types import AttachmentType
from allure_commons.utils import uuid4
from allure_pytest.listener import AllureListener
from dotenv import load_dotenv

from test.black_box.fynca import Fynca
from test.black_box.models import TestConfig

if TYPE_CHECKING:
    from collections.abc import Generator

    from playwright.sync_api import Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
_AUTH_DIR = _ROOT / "auth"
_STORAGE_STATE = _AUTH_DIR / "storage_state.json"

load_dotenv(_ROOT / ".env")

(_ROOT / "reports" / "allure-results").mkdir(parents=True, exist_ok=True)
(_ROOT / "reports" / "playwright").mkdir(parents=True, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _test_failed(request: pytest.FixtureRequest) -> bool:
    for when in ("setup", "call"):
        report = getattr(request.node, f"rep_{when}", None)
        if report is not None:
            return bool(report.failed)
    return True


def _allure_listener(config: pytest.Config) -> AllureListener | None:
    return next(
        (
            plugin
            for plugin in config.pluginmanager.get_plugins()
            if isinstance(plugin, AllureListener)
        ),
        None,
    )


def _attach_to_test(
    item: pytest.Item,
    *,
    name: str,
    attachment_type: AttachmentType,
    body: bytes | str | None = None,
    source: str | None = None,
) -> None:
    listener = _allure_listener(item.config)
    test_uuid = listener._cache.get(item.nodeid) if listener else None
    if listener is None or test_uuid is None:
        logger.info("Allure test uuid missing; skip %s attachment", name)
        return
    if body is not None:
        listener.allure_logger.attach_data(
            uuid4(),
            body,
            name=name,
            attachment_type=attachment_type,
            parent_uuid=test_uuid,
        )
        return
    if source:
        listener.allure_logger.attach_file(
            uuid4(),
            source,
            name=name,
            attachment_type=attachment_type,
            parent_uuid=test_uuid,
        )


def _attach_page_artifacts(page: Page, *, failed: bool, item: pytest.Item) -> None:
    video = page.video
    if failed:
        try:
            try:
                png = page.screenshot(full_page=True)
            except Exception:
                png = page.screenshot()
            _attach_to_test(
                item,
                name="screenshot",
                attachment_type=AttachmentType.PNG,
                body=png,
            )
        except Exception as exc:
            logger.info("Could not attach screenshot: %s", exc)
        try:
            _attach_to_test(
                item,
                name="page-url",
                attachment_type=AttachmentType.TEXT,
                body=page.url,
            )
        except Exception:
            pass
    try:
        page.close()
    except Exception:
        pass
    if video is None:
        return
    try:
        video_path = Path(video.path())
    except Exception:
        return
    if failed and video_path.exists():
        _attach_to_test(
            item,
            name="video",
            attachment_type=AttachmentType.WEBM,
            source=str(video_path),
        )
        return
    video_path.unlink(missing_ok=True)


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
def page(
    context: BrowserContext,
    request: pytest.FixtureRequest,
) -> Generator[Page]:
    pg = context.new_page()
    yield pg
    _attach_page_artifacts(pg, failed=_test_failed(request), item=request.node)


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
    request: pytest.FixtureRequest,
) -> Generator[Page]:
    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    yield page
    _attach_page_artifacts(page, failed=_test_failed(request), item=request.node)
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
