from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Response

logger = logging.getLogger(__name__)


def validate_response(response: Response) -> None:
    assert 200 <= response.status < 300, (
        f"Expected 2xx response, got {response.status} for {response.url}"
    )
