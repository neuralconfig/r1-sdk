"""
Integration test fixtures. All tests in this directory require live API credentials.
"""

import pytest

from r1_sdk import R1Client


def pytest_collection_modifyitems(config, items):
    """Auto-mark all tests in integration/ with @pytest.mark.integration."""
    for item in items:
        item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def live_client(credentials):
    """Provide a live R1Client instance for integration tests."""
    return R1Client(**credentials)
