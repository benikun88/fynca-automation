from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import allure
import pytest
from allure_commons.model2 import TestResult
from allure_commons.types import AttachmentType
from allure_commons.utils import uuid4
from allure_pytest.listener import AllureListener
from dotenv import load_dotenv
from slugify import slugify

from test.black_box.fynca import Fynca
from test.black_box.models import TestConfig

if TYPE_CHECKING:
    from collections.abc import Generator

    from playwright.sync_api import Page
    from pytest_playwright.pytest_playwright import CreateContextCallback

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
    if report.when in {"setup", "call"} and report.failed:
        _attach_failure_screenshot(item)
        return
    if report.when == "teardown" and _item_failed(item):
        _attach_playwright_artifacts(item)


def _item_failed(item: pytest.Item) -> bool:
    for when in ("setup", "call"):
        report = getattr(item, f"rep_{when}", None)
        if report is not None and report.failed:
            return True
    return False


def _attach_failure_screenshot(item: pytest.Item) -> None:
    page = item.funcargs.get("page") or item.funcargs.get("unauthenticated_page")
    if page is None:
        return
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


def _truncate_file_name(file_name: str) -> str:
    if len(file_name) < 256:
        return file_name
    return (
        f"{file_name[:100]}-{hashlib.sha256(file_name.encode()).hexdigest()[:7]}"
        f"-{file_name[-100:]}"
    )


def _playwright_artifact_dir(item: pytest.Item) -> Path:
    output_dir = Path(item.config.getoption("--output")).absolute()
    return output_dir / _truncate_file_name(slugify(item.nodeid))


def _attach_playwright_artifacts(item: pytest.Item) -> None:
    artifact_dir = _playwright_artifact_dir(item)
    if not artifact_dir.exists():
        logger.info("No Playwright artifact folder at %s", artifact_dir)
        return
    for png in sorted(artifact_dir.glob("test-failed-*.png")):
        _attach_to_test(
            item,
            name=png.stem,
            attachment_type=AttachmentType.PNG,
            source=str(png),
        )
    for video in sorted(artifact_dir.glob("video*.webm")):
        _attach_to_test(
            item,
            name="video",
            attachment_type=AttachmentType.WEBM,
            source=str(video),
        )


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
    test_result = listener.allure_logger.get_last_item(TestResult) if listener else None
    parent_uuid = getattr(test_result, "uuid", None)
    if listener is not None and parent_uuid is not None:
        if body is not None:
            listener.allure_logger.attach_data(
                uuid4(),
                body,
                name=name,
                attachment_type=attachment_type,
                parent_uuid=parent_uuid,
            )
            return
        if source:
            listener.allure_logger.attach_file(
                uuid4(),
                source,
                name=name,
                attachment_type=attachment_type,
                parent_uuid=parent_uuid,
            )
            return
    logger.info("Allure test uuid missing; attaching %s via allure.attach", name)
    if body is not None:
        allure.attach(body, name=name, attachment_type=attachment_type)
        return
    if source:
        allure.attach.file(source, name=name, attachment_type=attachment_type)


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
def context(new_context: CreateContextCallback, storage_state: Path):
    return new_context(storage_state=str(storage_state))


@pytest.fixture
def fynca(page: Page, test_config: TestConfig) -> Fynca:
    return Fynca(page, test_config.base_url, test_config.canvas_url)


@pytest.fixture
def canvas(fynca: Fynca):
    return fynca.goto_canvas()


@pytest.fixture
def unauthenticated_page(new_context: CreateContextCallback) -> Generator[Page]:
    context = new_context()
    page = context.new_page()
    yield page


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
