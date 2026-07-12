"""Pytest configuration for Boulder examples catalog."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: subprocess / CLI integration tests")
    config.addinivalue_line("markers", "slow: slow-running example solves")
