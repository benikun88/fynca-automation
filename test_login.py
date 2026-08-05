from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fynca import Fynca

logger = logging.getLogger(__name__)


@pytest.mark.login
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-LOGIN-001")
def test_login_page_is_visible(unauthenticated_fynca: Fynca) -> None:
    login_page = unauthenticated_fynca.goto_login()

    assert login_page.is_visible(), "Login welcome heading was not visible"


@pytest.mark.login
@pytest.mark.sanity
@pytest.mark.xray("FYNCA-LOGIN-002")
def test_login_identifier_field_is_visible(unauthenticated_fynca: Fynca) -> None:
    login_page = unauthenticated_fynca.goto_login()

    assert login_page.is_identifier_visible(), "Email/username field was not visible"
