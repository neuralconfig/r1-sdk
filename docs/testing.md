# Testing the R1 SDK

This document provides guidance on testing the RUCKUS One Python SDK.

## Prerequisites

1. A RUCKUS One account with API access
2. OAuth2 client credentials (client ID and client secret)
3. A tenant ID
4. Python 3.8 or higher

## Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/neuralconfig/r1-sdk.git
   cd r1-sdk
   ```

2. Create a virtual environment and install in development mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Set environment variables for your API credentials:
   ```bash
   export R1_CLIENT_ID="your-client-id"
   export R1_CLIENT_SECRET="your-client-secret"
   export R1_TENANT_ID="your-tenant-id"
   export R1_REGION="na"  # or "eu", "asia"
   ```

## Running Unit Tests

Unit tests use mocked API responses and don't require credentials:

```bash
pytest tests/unit/ -v
```

With coverage reporting:

```bash
pytest tests/unit/ -v --cov
```

## Running Integration Tests

Integration tests require live API credentials set via the environment variables above:

```bash
pytest tests/integration/ -v
```

## Writing Tests

### Unit Test Example

```python
"""Test venue operations."""

from unittest.mock import MagicMock
from r1_sdk import R1Client


def test_list_venues(mock_client):
    """Test listing venues."""
    mock_client._request = MagicMock(return_value=[{"id": "v1", "name": "HQ"}])
    result = mock_client.venues.list()
    assert len(result) == 1
    assert result[0]["name"] == "HQ"
```

### Integration Test Example

```python
"""Test live API connectivity."""

import pytest
from r1_sdk import R1Client


@pytest.mark.integration
def test_list_venues(r1_client):
    """Test listing venues against the live API."""
    venues = r1_client.venues.list()
    assert isinstance(venues, list)
```

## Troubleshooting

1. **Authentication errors**: Verify your `R1_CLIENT_ID`, `R1_CLIENT_SECRET`, and `R1_TENANT_ID` are correct and have the necessary permissions.

2. **Resource not found errors**: Verify that the IDs you're using (venue ID, AP serial, etc.) exist in your account.

3. **Enable verbose logging**: Set logging to DEBUG level to get detailed request/response information:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
