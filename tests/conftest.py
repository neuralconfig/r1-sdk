"""
Shared test fixtures for the R1 SDK test suite.
"""

import configparser
import os

import pytest


def _load_credentials():
    """Load credentials from config.ini or environment variables."""
    # Try config.ini first
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if 'credentials' in config:
            return {
                'client_id': config['credentials'].get('client_id'),
                'client_secret': config['credentials'].get('client_secret'),
                'tenant_id': config['credentials'].get('tenant_id'),
                'region': config['credentials'].get('region', 'na'),
            }

    # Fall back to environment variables
    client_id = os.environ.get('R1_CLIENT_ID')
    client_secret = os.environ.get('R1_CLIENT_SECRET')
    tenant_id = os.environ.get('R1_TENANT_ID')
    region = os.environ.get('R1_REGION', 'na')

    if client_id and client_secret and tenant_id:
        return {
            'client_id': client_id,
            'client_secret': client_secret,
            'tenant_id': tenant_id,
            'region': region,
        }

    return None


@pytest.fixture(scope="session")
def credentials():
    """Provide API credentials, or skip if unavailable."""
    creds = _load_credentials()
    if creds is None:
        pytest.skip("No API credentials available (need config.ini or R1_* env vars)")
    return creds
