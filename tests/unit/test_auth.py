"""Comprehensive unit tests for the Auth module."""

from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
import requests

from r1_sdk.auth import Auth, RUCKUS_REGIONS
from r1_sdk.exceptions import AuthenticationError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def auth():
    """Return an Auth instance with test credentials and default (na) region."""
    return Auth(
        client_id="test-id",
        client_secret="test-secret",
        tenant_id="test-tenant",
    )


@pytest.fixture
def auth_eu():
    """Return an Auth instance configured for the EU region."""
    return Auth(
        client_id="test-id",
        client_secret="test-secret",
        tenant_id="test-tenant",
        region="eu",
    )


@pytest.fixture
def auth_asia():
    """Return an Auth instance configured for the Asia region."""
    return Auth(
        client_id="test-id",
        client_secret="test-secret",
        tenant_id="test-tenant",
        region="asia",
    )


def _mock_auth_response(access_token="fake-jwt-token", expires_in=3600, status_code=200):
    """Build a MagicMock that behaves like a successful requests.Response."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = {
        "access_token": access_token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestAuthInit:
    """Tests for Auth.__init__."""

    def test_token_starts_as_none(self, auth):
        assert auth._token is None

    def test_token_expiry_starts_in_past_or_now(self, auth):
        # _token_expiry is set to datetime.now() at construction time,
        # so get_token() will always authenticate on first call.
        assert auth._token_expiry <= datetime.now()

    def test_stores_credentials(self, auth):
        assert auth.client_id == "test-id"
        assert auth.client_secret == "test-secret"
        assert auth.tenant_id == "test-tenant"

    def test_default_region_is_na(self, auth):
        assert auth.region == "na"

    def test_base_url_na(self, auth):
        assert auth.base_url == "https://api.ruckus.cloud"

    def test_base_url_eu(self, auth_eu):
        assert auth_eu.base_url == "https://api.eu.ruckus.cloud"

    def test_base_url_asia(self, auth_asia):
        assert auth_asia.base_url == "https://api.asia.ruckus.cloud"

    def test_unknown_region_falls_back_to_na(self):
        a = Auth("id", "secret", "tenant", region="mars")
        assert a.base_url == "https://api.ruckus.cloud"


# ---------------------------------------------------------------------------
# Region mapping
# ---------------------------------------------------------------------------

class TestRegionMapping:
    """Tests for the RUCKUS_REGIONS constant."""

    def test_contains_na(self):
        assert "na" in RUCKUS_REGIONS

    def test_contains_eu(self):
        assert "eu" in RUCKUS_REGIONS

    def test_contains_asia(self):
        assert "asia" in RUCKUS_REGIONS

    def test_na_value(self):
        assert RUCKUS_REGIONS["na"] == "api.ruckus.cloud"

    def test_eu_value(self):
        assert RUCKUS_REGIONS["eu"] == "api.eu.ruckus.cloud"

    def test_asia_value(self):
        assert RUCKUS_REGIONS["asia"] == "api.asia.ruckus.cloud"

    def test_exactly_three_regions(self):
        assert len(RUCKUS_REGIONS) == 3


# ---------------------------------------------------------------------------
# _authenticate
# ---------------------------------------------------------------------------

class TestAuthenticate:
    """Tests for Auth._authenticate (the low-level token fetch)."""

    @patch("r1_sdk.auth.requests.post")
    def test_sends_correct_post_request(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response()

        auth._authenticate()

        mock_post.assert_called_once_with(
            "https://api.ruckus.cloud/oauth2/token/test-tenant",
            data={
                "grant_type": "client_credentials",
                "client_id": "test-id",
                "client_secret": "test-secret",
            },
        )

    @patch("r1_sdk.auth.requests.post")
    def test_returns_token_and_expiry(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(
            access_token="my-token", expires_in=3600
        )

        token, expiry = auth._authenticate()

        assert token == "my-token"
        # Expiry should be approximately now + 3600 - 300 = 3300 seconds
        expected_min = datetime.now() + timedelta(seconds=3200)
        expected_max = datetime.now() + timedelta(seconds=3400)
        assert expected_min <= expiry <= expected_max

    @patch("r1_sdk.auth.requests.post")
    def test_uses_default_expires_in_when_missing(self, mock_post, auth):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "tok"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        token, expiry = auth._authenticate()

        assert token == "tok"
        # Default is 3600; safety margin is 300 => 3300 seconds from now
        expected = datetime.now() + timedelta(seconds=3300)
        assert abs((expiry - expected).total_seconds()) < 5

    @patch("r1_sdk.auth.requests.post")
    def test_raises_on_http_error(self, mock_post, auth):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_resp

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            auth._authenticate()

    @patch("r1_sdk.auth.requests.post")
    def test_raises_on_connection_error(self, mock_post, auth):
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            auth._authenticate()

    @patch("r1_sdk.auth.requests.post")
    def test_raises_on_timeout(self, mock_post, auth):
        mock_post.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            auth._authenticate()

    @patch("r1_sdk.auth.requests.post")
    def test_raises_when_no_access_token_in_response(self, mock_post, auth):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"token_type": "Bearer"}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        with pytest.raises(AuthenticationError, match="No access token in response"):
            auth._authenticate()

    @patch("r1_sdk.auth.requests.post")
    def test_url_includes_correct_tenant_id(self, mock_post):
        mock_post.return_value = _mock_auth_response()
        a = Auth("id", "secret", "my-tenant-123", region="eu")

        a._authenticate()

        url_used = mock_post.call_args[0][0]
        assert url_used == "https://api.eu.ruckus.cloud/oauth2/token/my-tenant-123"


# ---------------------------------------------------------------------------
# get_token
# ---------------------------------------------------------------------------

class TestGetToken:
    """Tests for Auth.get_token (caching logic)."""

    @patch("r1_sdk.auth.requests.post")
    def test_calls_authenticate_when_token_is_none(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="first-token")

        assert auth._token is None
        token = auth.get_token()

        assert token == "first-token"
        mock_post.assert_called_once()

    @patch("r1_sdk.auth.requests.post")
    def test_returns_cached_token_when_not_expired(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="cached-token")

        # First call to populate the cache
        first_token = auth.get_token()
        assert first_token == "cached-token"
        assert mock_post.call_count == 1

        # Second call should use the cache
        second_token = auth.get_token()
        assert second_token == "cached-token"
        assert mock_post.call_count == 1  # no additional call

    @patch("r1_sdk.auth.requests.post")
    def test_re_authenticates_when_token_expired(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="token-1")

        auth.get_token()
        assert mock_post.call_count == 1

        # Simulate token expiry by setting _token_expiry in the past
        auth._token_expiry = datetime.now() - timedelta(seconds=1)

        mock_post.return_value = _mock_auth_response(access_token="token-2")
        token = auth.get_token()

        assert token == "token-2"
        assert mock_post.call_count == 2

    @patch("r1_sdk.auth.requests.post")
    def test_propagates_authentication_error(self, mock_post, auth):
        mock_post.side_effect = requests.ConnectionError("nope")

        with pytest.raises(AuthenticationError):
            auth.get_token()


# ---------------------------------------------------------------------------
# refresh_token
# ---------------------------------------------------------------------------

class TestRefreshToken:
    """Tests for Auth.refresh_token (forced refresh)."""

    @patch("r1_sdk.auth.requests.post")
    def test_updates_internal_token(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="old-token")
        auth.get_token()  # populate cache
        assert auth._token == "old-token"

        mock_post.return_value = _mock_auth_response(access_token="new-token")
        auth.refresh_token()

        assert auth._token == "new-token"

    @patch("r1_sdk.auth.requests.post")
    def test_updates_token_expiry(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(expires_in=7200)

        auth.refresh_token()

        expected_min = datetime.now() + timedelta(seconds=6800)
        assert auth._token_expiry >= expected_min

    @patch("r1_sdk.auth.requests.post")
    def test_refresh_always_calls_authenticate(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response()

        auth.get_token()
        assert mock_post.call_count == 1

        auth.refresh_token()
        assert mock_post.call_count == 2  # forced, even though token is valid

    @patch("r1_sdk.auth.requests.post")
    def test_propagates_authentication_error(self, mock_post, auth):
        mock_post.side_effect = requests.ConnectionError("nope")

        with pytest.raises(AuthenticationError):
            auth.refresh_token()


# ---------------------------------------------------------------------------
# get_auth_headers
# ---------------------------------------------------------------------------

class TestGetAuthHeaders:
    """Tests for Auth.get_auth_headers."""

    @patch("r1_sdk.auth.requests.post")
    def test_returns_correct_dict(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="hdr-token")

        headers = auth.get_auth_headers()

        assert headers == {
            "Authorization": "Bearer hdr-token",
            "Content-Type": "application/json",
        }

    @patch("r1_sdk.auth.requests.post")
    def test_header_token_matches_get_token(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="same-token")

        token = auth.get_token()
        headers = auth.get_auth_headers()

        assert headers["Authorization"] == f"Bearer {token}"

    @patch("r1_sdk.auth.requests.post")
    def test_uses_cached_token(self, mock_post, auth):
        mock_post.return_value = _mock_auth_response(access_token="cached")

        auth.get_auth_headers()
        auth.get_auth_headers()

        assert mock_post.call_count == 1  # only one auth call
