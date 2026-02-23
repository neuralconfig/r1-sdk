"""Shared fixtures for unit tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_client():
    """Create a mock R1Client for module tests."""
    return MagicMock()
