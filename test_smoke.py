from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fynca import Fynca

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-HOME-001")
def test_authenticated_home_loads(fynca: Fynca) -> None:
    home = fynca.goto_home()

    assert home.is_authenticated(), (
        f"Expected authenticated session, got {home.get_url()}"
    )
