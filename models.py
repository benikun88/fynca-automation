from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestConfig:
    base_url: str
    email: str
    password: str
    canvas_url: str
