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
    # New canonical names
    assert client.venues is not None
    assert client.aps is not None
    assert client.switches is not None
    assert client.wifi_networks is not None
    assert client.vlan_pools is not None
    assert client.dpsk is not None
    assert client.identities is not None
    assert client.identity_groups is not None
    assert client.l3_acl_policies is not None
    assert client.cli_templates is not None
    assert client.switch_profiles is not None
    # Backward compat aliases
    assert client.wlans is client.wifi_networks
    assert client.vlans is client.vlan_pools
    assert client.l3acl is client.l3_acl_policies


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


# ---------------------------------------------------------------------------
# Tests for request(), _handle_error_response(), and convenience methods
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock, patch, call


@pytest.fixture
def client():
    """Return an R1Client with a mocked auth object."""
    c = R1Client(client_id="x", client_secret="y", tenant_id="z")
    c.auth = MagicMock()
    c.auth.get_auth_headers.return_value = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json",
    }
    return c


# --- request() basic behaviour -------------------------------------------

@patch("r1_sdk.client.requests.request")
def test_request_builds_correct_url(mock_req, client):
    """request() should join base_url with the path."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"ok": true}'
    mock_resp.json.return_value = {"ok": True}
    mock_req.return_value = mock_resp

    client.request("GET", "/v1/venues")

    called_url = mock_req.call_args[1]["url"]
    assert called_url.startswith("https://")
    assert called_url.endswith("/v1/venues")


@patch("r1_sdk.client.requests.request")
def test_request_passes_all_arguments(mock_req, client):
    """request() should forward method, params, data, json, and headers."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"ok": true}'
    mock_resp.json.return_value = {"ok": True}
    mock_req.return_value = mock_resp

    client.request(
        "POST",
        "/v1/venues",
        params={"page": 1},
        data={"field": "val"},
        json_data={"name": "test"},
        headers={"X-Custom": "yes"},
    )

    _, kwargs = mock_req.call_args
    assert kwargs["method"] == "POST"
    assert kwargs["params"] == {"page": 1}
    assert kwargs["data"] == {"field": "val"}
    assert kwargs["json"] == {"name": "test"}
    assert kwargs["headers"]["X-Custom"] == "yes"


@patch("r1_sdk.client.requests.request")
def test_request_merges_custom_headers(mock_req, client):
    """Custom headers should be merged on top of auth headers."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"ok": true}'
    mock_resp.json.return_value = {"ok": True}
    mock_req.return_value = mock_resp

    client.request("GET", "/v1/test", headers={"Accept": "text/csv"})

    sent_headers = mock_req.call_args[1]["headers"]
    assert sent_headers["Authorization"] == "Bearer test-token"
    assert sent_headers["Accept"] == "text/csv"


# --- request() success responses ----------------------------------------

@patch("r1_sdk.client.requests.request")
def test_request_returns_parsed_json(mock_req, client):
    """200 with JSON Content-Type should return parsed dict."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json; charset=utf-8"}
    mock_resp.content = b'{"id": 42}'
    mock_resp.json.return_value = {"id": 42}
    mock_req.return_value = mock_resp

    result = client.request("GET", "/v1/thing")
    assert result == {"id": 42}


@patch("r1_sdk.client.requests.request")
def test_request_returns_raw_response(mock_req, client):
    """raw_response=True should return the response object itself."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_req.return_value = mock_resp

    result = client.request("GET", "/v1/thing", raw_response=True)
    assert result is mock_resp


@patch("r1_sdk.client.requests.request")
def test_request_returns_content_for_non_json(mock_req, client):
    """Non-JSON 200 responses should return response.content bytes."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "text/plain"}
    mock_resp.content = b"hello"
    mock_req.return_value = mock_resp

    result = client.request("GET", "/v1/thing")
    assert result == b"hello"


@patch("r1_sdk.client.requests.request")
def test_request_returns_content_when_empty_body(mock_req, client):
    """Empty content with JSON content-type should return b'' (falsy content)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b""
    mock_req.return_value = mock_resp

    result = client.request("GET", "/v1/thing")
    assert result == b""


# --- request() 401 auto-refresh -----------------------------------------

@patch("r1_sdk.client.requests.request")
def test_request_refreshes_on_401_and_retries(mock_req, client):
    """On a 401, request() should refresh the token and retry once."""
    first_resp = MagicMock()
    first_resp.status_code = 401

    second_resp = MagicMock()
    second_resp.status_code = 200
    second_resp.headers = {"Content-Type": "application/json"}
    second_resp.content = b'{"retried": true}'
    second_resp.json.return_value = {"retried": True}

    mock_req.side_effect = [first_resp, second_resp]

    result = client.request("GET", "/v1/thing")

    client.auth.refresh_token.assert_called_once()
    assert mock_req.call_count == 2
    assert result == {"retried": True}


@patch("r1_sdk.client.requests.request")
def test_request_401_retry_merges_custom_headers(mock_req, client):
    """On 401 retry, custom headers should be re-merged with fresh auth headers."""
    first_resp = MagicMock()
    first_resp.status_code = 401

    second_resp = MagicMock()
    second_resp.status_code = 200
    second_resp.headers = {"Content-Type": "application/json"}
    second_resp.content = b'{"ok": true}'
    second_resp.json.return_value = {"ok": True}

    mock_req.side_effect = [first_resp, second_resp]

    # After refresh, auth returns new token
    client.auth.get_auth_headers.side_effect = [
        {"Authorization": "Bearer old-token", "Content-Type": "application/json"},
        {"Authorization": "Bearer new-token", "Content-Type": "application/json"},
    ]

    client.request("GET", "/v1/thing", headers={"X-Trace": "abc"})

    # The retry call should have the new token AND the custom header
    retry_headers = mock_req.call_args_list[1][1]["headers"]
    assert retry_headers["Authorization"] == "Bearer new-token"
    assert retry_headers["X-Trace"] == "abc"


# --- request() error delegation ------------------------------------------

@patch("r1_sdk.client.requests.request")
def test_request_delegates_error_response(mock_req, client):
    """Non-2xx responses (after possible 401 retry) should raise via _handle_error_response."""
    from r1_sdk.exceptions import ResourceNotFoundError

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"message": "not found"}'
    mock_resp.json.return_value = {"message": "not found"}
    mock_req.return_value = mock_resp

    with pytest.raises(ResourceNotFoundError):
        client.request("GET", "/v1/missing")


@patch("r1_sdk.client.requests.request")
def test_request_wraps_request_exception(mock_req, client):
    """requests.RequestException should be wrapped in APIError."""
    from r1_sdk.exceptions import APIError

    mock_req.side_effect = __import__("requests").ConnectionError("refused")

    with pytest.raises(APIError, match="Request failed"):
        client.request("GET", "/v1/thing")


# --- _handle_error_response() -------------------------------------------

def _make_error_response(status_code, content_type="application/json", body=None, text=""):
    """Helper to build a mock response for error handling tests."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {"Content-Type": content_type}
    if body is not None:
        resp.content = b"present"
        resp.json.return_value = body
    else:
        resp.content = b""
    resp.text = text
    return resp


def test_handle_error_401(client):
    from r1_sdk.exceptions import AuthenticationError
    resp = _make_error_response(401, body={"message": "bad token"})
    with pytest.raises(AuthenticationError, match="bad token"):
        client._handle_error_response(resp)


def test_handle_error_404(client):
    from r1_sdk.exceptions import ResourceNotFoundError
    resp = _make_error_response(404, body={"message": "gone"})
    with pytest.raises(ResourceNotFoundError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "gone"


def test_handle_error_400(client):
    from r1_sdk.exceptions import ValidationError
    resp = _make_error_response(400, body={"message": "bad field"})
    with pytest.raises(ValidationError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "bad field"


def test_handle_error_429(client):
    from r1_sdk.exceptions import RateLimitError
    resp = _make_error_response(429, body={"message": "slow down"})
    with pytest.raises(RateLimitError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "slow down"


def test_handle_error_500(client):
    from r1_sdk.exceptions import ServerError
    resp = _make_error_response(500, body={"error": "kaboom"})
    with pytest.raises(ServerError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "kaboom"


def test_handle_error_503(client):
    from r1_sdk.exceptions import ServerError
    resp = _make_error_response(503, body={"error": "unavailable"})
    with pytest.raises(ServerError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.status_code == 503


def test_handle_error_other_status(client):
    """An unrecognised status code (e.g. 418) should raise generic APIError."""
    from r1_sdk.exceptions import APIError
    resp = _make_error_response(418, body={"message": "I'm a teapot"})
    with pytest.raises(APIError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.status_code == 418


def test_handle_error_extracts_json_message(client):
    """Should prefer 'message' key in JSON body for error detail."""
    from r1_sdk.exceptions import ValidationError
    resp = _make_error_response(400, body={"message": "name required", "code": 1234})
    with pytest.raises(ValidationError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "name required"


def test_handle_error_extracts_json_error_key(client):
    """Should fall back to 'error' key when 'message' is absent."""
    from r1_sdk.exceptions import ValidationError
    resp = _make_error_response(400, body={"error": "invalid"})
    with pytest.raises(ValidationError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "invalid"


def test_handle_error_non_json_response(client):
    """When .json() raises ValueError, error_detail should be response.text."""
    from r1_sdk.exceptions import ServerError
    resp = MagicMock()
    resp.status_code = 500
    resp.headers = {"Content-Type": "application/json"}
    resp.content = b"not json"
    resp.json.side_effect = ValueError("bad json")
    resp.text = "Internal Server Error"

    with pytest.raises(ServerError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail == "Internal Server Error"


def test_handle_error_plain_text_content_type(client):
    """Non-JSON content type should leave error_detail as None."""
    from r1_sdk.exceptions import ServerError
    resp = _make_error_response(500, content_type="text/plain", body=None)
    with pytest.raises(ServerError) as exc_info:
        client._handle_error_response(resp)
    assert exc_info.value.detail is None


# --- Convenience methods --------------------------------------------------

@patch("r1_sdk.client.requests.request")
def test_get_delegates(mock_req, client):
    """get() should call request('GET', ...)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'[]'
    mock_resp.json.return_value = []
    mock_req.return_value = mock_resp

    result = client.get("/v1/venues", params={"limit": 10})
    assert mock_req.call_args[1]["method"] == "GET"
    assert result == []


@patch("r1_sdk.client.requests.request")
def test_post_delegates(mock_req, client):
    """post() should call request('POST', ...) with data mapped to json_data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"id": 1}'
    mock_resp.json.return_value = {"id": 1}
    mock_req.return_value = mock_resp

    result = client.post("/v1/venues", data={"name": "HQ"})
    assert mock_req.call_args[1]["method"] == "POST"
    assert mock_req.call_args[1]["json"] == {"name": "HQ"}
    assert result == {"id": 1}


@patch("r1_sdk.client.requests.request")
def test_put_delegates(mock_req, client):
    """put() should call request('PUT', ...) with data mapped to json_data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"updated": true}'
    mock_resp.json.return_value = {"updated": True}
    mock_req.return_value = mock_resp

    result = client.put("/v1/venues/1", data={"name": "HQ2"})
    assert mock_req.call_args[1]["method"] == "PUT"
    assert mock_req.call_args[1]["json"] == {"name": "HQ2"}
    assert result == {"updated": True}


@patch("r1_sdk.client.requests.request")
def test_patch_delegates(mock_req, client):
    """patch() should call request('PATCH', ...) with data mapped to json_data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"patched": true}'
    mock_resp.json.return_value = {"patched": True}
    mock_req.return_value = mock_resp

    result = client.patch("/v1/venues/1", data={"name": "HQ3"})
    assert mock_req.call_args[1]["method"] == "PATCH"
    assert mock_req.call_args[1]["json"] == {"name": "HQ3"}
    assert result == {"patched": True}


@patch("r1_sdk.client.requests.request")
def test_delete_delegates(mock_req, client):
    """delete() should call request('DELETE', ...)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.headers = {"Content-Type": ""}
    mock_resp.content = b""
    mock_req.return_value = mock_resp

    result = client.delete("/v1/venues/1")
    assert mock_req.call_args[1]["method"] == "DELETE"
    assert result == b""
