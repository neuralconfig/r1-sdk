# Testing the RUCKUS One SDK

This document provides guidance on testing the RUCKUS One Python SDK.

## Prerequisites

Before you begin testing, you'll need:

1. A RUCKUS One account with API access
2. OAuth2 client credentials (client ID and client secret)
3. A tenant ID
4. A test venue with at least one AP and/or switch
5. Python 3.7 or higher installed on your system

## Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/neuralconfig/r1-api.git
   cd r1-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the SDK in development mode:
   ```bash
   pip install -e .
   ```

4. Set environment variables for your API credentials:
   ```bash
   export RUCKUS_API_REGION="na"  # or "eu", "asia"
   export RUCKUS_API_CLIENT_ID="your-client-id"
   export RUCKUS_API_CLIENT_SECRET="your-client-secret"
   export RUCKUS_API_TENANT_ID="your-tenant-id"
   ```

## Running the Basic Example

Run the basic example to test connectivity and basic operations:

```bash
python examples/basic_usage.py
```

This should:
1. Authenticate with the RUCKUS One API
2. List venues in your account
3. Get details of the first venue
4. List APs in that venue
5. List WLANs in your account

## Testing with the CLI Tool

The SDK includes a command-line interface for testing. Here are some example commands:

### List Venues

```bash
./bin/ruckus-cli venue list --page-size 5
```

### Get Venue Details

```bash
./bin/ruckus-cli venue get --id YOUR_VENUE_ID
```

### List APs in a Venue

```bash
./bin/ruckus-cli ap list --venue-id YOUR_VENUE_ID
```

### List WLANs

```bash
./bin/ruckus-cli wlan list
```

## Writing Your Own Tests

You can create additional test scripts in the `examples/` directory. For example:

### Testing AP Operations

Create a file `examples/test_ap_operations.py`:

```python
"""
Test AP operations.
"""

import os
import sys
import logging

# Add the parent directory to the path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ruckus_one import RuckusOneClient
from ruckus_one.exceptions import APIError

# Set up logging
logging.basicConfig(level=logging.INFO)

# API credentials from environment variables
API_REGION = os.environ.get("RUCKUS_API_REGION", "na")
API_CLIENT_ID = os.environ.get("RUCKUS_API_CLIENT_ID")
API_CLIENT_SECRET = os.environ.get("RUCKUS_API_CLIENT_SECRET")
API_TENANT_ID = os.environ.get("RUCKUS_API_TENANT_ID")

# Test venue and AP information (replace with your own)
TEST_VENUE_ID = "your-venue-id"
TEST_AP_SERIAL = "your-ap-serial"

def main():
    """Test AP operations."""
    try:
        # Initialize client
        client = RuckusOneClient(
            client_id=API_CLIENT_ID,
            client_secret=API_CLIENT_SECRET,
            tenant_id=API_TENANT_ID,
            region=API_REGION
        )
        
        # Get AP details
        ap = client.aps.get(TEST_VENUE_ID, TEST_AP_SERIAL)
        logging.info(f"AP details: {ap['name']} (Model: {ap['model']})")
        
        # Get AP radio settings
        radio_settings = client.aps.get_radio_settings(TEST_VENUE_ID, TEST_AP_SERIAL)
        logging.info(f"Radio settings: {radio_settings}")
        
        # Get AP statistics
        stats = client.aps.get_statistics(TEST_VENUE_ID, TEST_AP_SERIAL)
        logging.info(f"AP statistics: {stats}")
        
    except APIError as e:
        logging.error(f"API error: {e}")
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

## Troubleshooting

If you encounter issues during testing:

1. **Authentication errors**: Double-check your OAuth2 client credentials and tenant ID. Make sure they have the necessary permissions.

2. **Resource not found errors**: Verify that the IDs you're using (venue ID, AP serial, etc.) are correct.

3. **API errors**: Check the error message for details. The SDK provides specific exceptions to help diagnose problems.

4. **Enable verbose logging**: Use the `--verbose` flag with CLI commands or set logging to DEBUG level in your scripts to get more detailed information.

## Next Steps

Once basic testing is complete, you can:

1. Add more comprehensive tests for each module
2. Create more complex scripts that combine multiple operations
3. Develop automated tests with pytest
4. Build your own applications on top of the SDK