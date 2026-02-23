"""Unit tests for R1Client construction and factory methods."""

import os
import tempfile

import pytest

from r1_sdk import R1Client
from r1_sdk.exceptions import R1Error


def test_missing_credentials_raises():
    with pytest.raises(ValueError):
        R1Client(client_id="", client_secret="", tenant_id="")


def test_from_config_reads_ini():
    """from_config() should read credentials from an INI file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("[credentials]\n")
        f.write("client_id = test-id\n")
        f.write("client_secret = test-secret\n")
        f.write("tenant_id = test-tenant\n")
        f.write("region = eu\n")
        f.flush()

        try:
            client = R1Client.from_config(f.name)
            assert client.tenant_id == "test-tenant"
            assert "eu" in client.base_url
        finally:
            os.unlink(f.name)


def test_from_env_reads_environment(monkeypatch):
    """from_env() should read credentials from environment variables."""
    monkeypatch.setenv("R1_CLIENT_ID", "env-id")
    monkeypatch.setenv("R1_CLIENT_SECRET", "env-secret")
    monkeypatch.setenv("R1_TENANT_ID", "env-tenant")
    monkeypatch.setenv("R1_REGION", "asia")

    client = R1Client.from_env()
    assert client.tenant_id == "env-tenant"
    assert "asia" in client.base_url


def test_from_env_missing_var_raises(monkeypatch):
    """from_env() should raise KeyError if required env var is missing."""
    monkeypatch.delenv("R1_CLIENT_ID", raising=False)
    monkeypatch.delenv("R1_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("R1_TENANT_ID", raising=False)

    with pytest.raises(KeyError):
        R1Client.from_env()


def test_modules_initialized():
    """Client should auto-initialize all modules."""
    client = R1Client(client_id="x", client_secret="y", tenant_id="z")
    assert client.venues is not None
    assert client.aps is not None
    assert client.switches is not None
    assert client.wlans is not None
    assert client.vlans is not None
    assert client.dpsk is not None
    assert client.identities is not None
    assert client.identity_groups is not None
    assert client.l3acl is not None
    assert client.cli_templates is not None
    assert client.switch_profiles is not None


def test_default_region():
    """Default region should be 'na'."""
    client = R1Client(client_id="x", client_secret="y", tenant_id="z")
    assert "api.ruckus.cloud" in client.base_url


def test_exception_hierarchy():
    """R1Error should be the base for all SDK exceptions."""
    from r1_sdk.exceptions import (
        AuthenticationError, APIError, ResourceNotFoundError,
        ValidationError, RateLimitError, ServerError
    )
    assert issubclass(AuthenticationError, R1Error)
    assert issubclass(APIError, R1Error)
    assert issubclass(ResourceNotFoundError, APIError)
    assert issubclass(ValidationError, APIError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(ServerError, APIError)
