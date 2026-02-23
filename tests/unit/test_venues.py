"""Comprehensive unit tests for the Venues module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.venues import Venues


@pytest.fixture
def venues(mock_client):
    """Create a Venues instance backed by a mock client."""
    return Venues(mock_client)


# ── list ────────────────────────────────────────────────────────────────────


class TestList:
    """Tests for Venues.list()."""

    def test_posts_to_correct_endpoint(self, venues):
        venues.list()
        venues.client.post.assert_called_once()
        args, kwargs = venues.client.post.call_args
        assert args[0] == "/venues/query"

    def test_default_query_data(self, venues):
        venues.list()
        expected = {"pageSize": 100, "page": 0, "sortOrder": "ASC"}
        venues.client.post.assert_called_once_with("/venues/query", data=expected)

    def test_search_string_included(self, venues):
        venues.list(search_string="lobby")
        data = venues.client.post.call_args[1]["data"]
        assert data["searchString"] == "lobby"

    def test_custom_page_size_and_page(self, venues):
        venues.list(page_size=50, page=3)
        data = venues.client.post.call_args[1]["data"]
        assert data["pageSize"] == 50
        assert data["page"] == 3

    def test_sort_field_included(self, venues):
        venues.list(sort_field="name")
        data = venues.client.post.call_args[1]["data"]
        assert data["sortField"] == "name"

    def test_sort_order_uppercased(self, venues):
        venues.list(sort_order="desc")
        data = venues.client.post.call_args[1]["data"]
        assert data["sortOrder"] == "DESC"

    def test_data_overrides_all_params(self, venues):
        custom = {"custom": "payload", "nested": {"a": 1}}
        venues.list(search_string="ignored", page_size=999, data=custom)
        venues.client.post.assert_called_once_with("/venues/query", data=custom)

    def test_returns_client_response(self, venues):
        venues.client.post.return_value = {"data": [], "totalCount": 0}
        result = venues.list()
        assert result == {"data": [], "totalCount": 0}

    def test_propagates_unexpected_exception(self, venues):
        venues.client.post.side_effect = RuntimeError("connection lost")
        with pytest.raises(RuntimeError, match="connection lost"):
            venues.list()

    def test_no_search_string_key_when_none(self, venues):
        venues.list()
        data = venues.client.post.call_args[1]["data"]
        assert "searchString" not in data

    def test_no_sort_field_key_when_none(self, venues):
        venues.list()
        data = venues.client.post.call_args[1]["data"]
        assert "sortField" not in data

    def test_empty_search_string_not_included(self, venues):
        """Empty string is falsy, so searchString should be omitted."""
        venues.list(search_string="")
        data = venues.client.post.call_args[1]["data"]
        assert "searchString" not in data


# ── get ─────────────────────────────────────────────────────────────────────


class TestGet:
    """Tests for Venues.get()."""

    def test_gets_correct_endpoint(self, venues):
        venue_id = "abc-123"
        venues.get(venue_id)
        venues.client.get.assert_called_once_with(f"/venues/{venue_id}")

    def test_returns_venue_dict(self, venues):
        expected = {"id": "abc-123", "name": "Main Office"}
        venues.client.get.return_value = expected
        assert venues.get("abc-123") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-id not found"):
            venues.get("bad-id")

    def test_404_preserves_status_code(self, venues):
        venues.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.get("bad-id")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.get.side_effect = ValueError("unexpected")
        with pytest.raises(ValueError, match="unexpected"):
            venues.get("x")


# ── create ──────────────────────────────────────────────────────────────────


class TestCreate:
    """Tests for Venues.create()."""

    def test_posts_to_correct_endpoint(self, venues):
        venues.create(name="HQ", address={"city": "Denver"})
        args, kwargs = venues.client.post.call_args
        assert args[0] == "/venues"

    def test_required_fields_in_payload(self, venues):
        venues.create(name="HQ", address={"city": "Denver"})
        data = venues.client.post.call_args[1]["data"]
        assert data["name"] == "HQ"
        assert data["address"] == {"city": "Denver"}

    def test_optional_description(self, venues):
        venues.create(name="HQ", address={}, description="Main building")
        data = venues.client.post.call_args[1]["data"]
        assert data["description"] == "Main building"

    def test_optional_timezone(self, venues):
        venues.create(name="HQ", address={}, timezone="America/Denver")
        data = venues.client.post.call_args[1]["data"]
        assert data["timezone"] == "America/Denver"

    def test_description_omitted_when_none(self, venues):
        venues.create(name="HQ", address={})
        data = venues.client.post.call_args[1]["data"]
        assert "description" not in data

    def test_timezone_omitted_when_none(self, venues):
        venues.create(name="HQ", address={})
        data = venues.client.post.call_args[1]["data"]
        assert "timezone" not in data

    def test_kwargs_merged_into_payload(self, venues):
        venues.create(name="HQ", address={}, country="US", capacity=200)
        data = venues.client.post.call_args[1]["data"]
        assert data["country"] == "US"
        assert data["capacity"] == 200

    def test_returns_created_venue(self, venues):
        expected = {"id": "new-1", "name": "HQ"}
        venues.client.post.return_value = expected
        result = venues.create(name="HQ", address={})
        assert result == expected

    def test_empty_description_not_included(self, venues):
        """Empty string is falsy, so description should be omitted."""
        venues.create(name="HQ", address={}, description="")
        data = venues.client.post.call_args[1]["data"]
        assert "description" not in data

    def test_empty_timezone_not_included(self, venues):
        """Empty string is falsy, so timezone should be omitted."""
        venues.create(name="HQ", address={}, timezone="")
        data = venues.client.post.call_args[1]["data"]
        assert "timezone" not in data


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdate:
    """Tests for Venues.update()."""

    def test_puts_to_correct_endpoint(self, venues):
        venues.update("abc-123", name="New Name")
        venues.client.put.assert_called_once()
        args, _ = venues.client.put.call_args
        assert args[0] == "/venues/abc-123"

    def test_kwargs_sent_as_data(self, venues):
        venues.update("abc-123", name="Renamed", description="Updated")
        data = venues.client.put.call_args[1]["data"]
        assert data == {"name": "Renamed", "description": "Updated"}

    def test_empty_kwargs_sends_empty_dict(self, venues):
        venues.update("abc-123")
        data = venues.client.put.call_args[1]["data"]
        assert data == {}

    def test_returns_updated_venue(self, venues):
        expected = {"id": "abc-123", "name": "Renamed"}
        venues.client.put.return_value = expected
        assert venues.update("abc-123", name="Renamed") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID gone-id not found"):
            venues.update("gone-id", name="x")

    def test_404_preserves_status_code(self, venues):
        venues.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.update("gone-id", name="x")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.put.side_effect = ConnectionError("timeout")
        with pytest.raises(ConnectionError, match="timeout"):
            venues.update("abc-123", name="x")


# ── delete ──────────────────────────────────────────────────────────────────


class TestDelete:
    """Tests for Venues.delete()."""

    def test_deletes_correct_endpoint(self, venues):
        venues.delete("abc-123")
        venues.client.delete.assert_called_once_with("/venues/abc-123")

    def test_returns_none(self, venues):
        venues.client.delete.return_value = None
        result = venues.delete("abc-123")
        assert result is None

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID gone-id not found"):
            venues.delete("gone-id")

    def test_404_preserves_status_code(self, venues):
        venues.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.delete("gone-id")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.delete.side_effect = PermissionError("forbidden")
        with pytest.raises(PermissionError, match="forbidden"):
            venues.delete("abc-123")


# ── get_aps ─────────────────────────────────────────────────────────────────


class TestGetAps:
    """Tests for Venues.get_aps()."""

    def test_gets_correct_endpoint(self, venues):
        venues.get_aps("v-1")
        venues.client.get.assert_called_once_with("/venues/v-1/aps")

    def test_returns_ap_list(self, venues):
        expected = [{"serial": "AP001"}, {"serial": "AP002"}]
        venues.client.get.return_value = expected
        assert venues.get_aps("v-1") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-v not found"):
            venues.get_aps("bad-v")

    def test_404_preserves_status_code(self, venues):
        venues.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.get_aps("bad-v")
        assert exc_info.value.status_code == 404

    def test_kwargs_accepted_without_error(self, venues):
        """kwargs are accepted (stored in params) but not currently passed to client.get."""
        venues.get_aps("v-1", status="online", limit=50)
        venues.client.get.assert_called_once_with("/venues/v-1/aps")

    def test_non_404_exception_propagates(self, venues):
        venues.client.get.side_effect = TimeoutError("slow")
        with pytest.raises(TimeoutError, match="slow"):
            venues.get_aps("v-1")


# ── get_switches ────────────────────────────────────────────────────────────


class TestGetSwitches:
    """Tests for Venues.get_switches()."""

    def test_posts_to_correct_endpoint(self, venues):
        venues.get_switches("v-1")
        venues.client.post.assert_called_once()
        args, _ = venues.client.post.call_args
        assert args[0] == "/venues/v-1/switches/query"

    def test_empty_kwargs_sends_empty_dict(self, venues):
        venues.get_switches("v-1")
        data = venues.client.post.call_args[1]["data"]
        assert data == {}

    def test_kwargs_sent_as_data(self, venues):
        venues.get_switches("v-1", pageSize=50, page=2)
        data = venues.client.post.call_args[1]["data"]
        assert data == {"pageSize": 50, "page": 2}

    def test_returns_switch_data(self, venues):
        expected = {"data": [{"name": "SW1"}], "totalCount": 1}
        venues.client.post.return_value = expected
        assert venues.get_switches("v-1") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-v not found"):
            venues.get_switches("bad-v")

    def test_404_preserves_status_code(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.get_switches("bad-v")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.post.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            venues.get_switches("v-1")


# ── get_wlans ───────────────────────────────────────────────────────────────


class TestGetWlans:
    """Tests for Venues.get_wlans()."""

    def test_posts_to_correct_endpoint(self, venues):
        venues.get_wlans("v-1")
        venues.client.post.assert_called_once()
        args, _ = venues.client.post.call_args
        assert args[0] == "/venues/v-1/wifiNetworks/query"

    def test_empty_kwargs_sends_empty_dict(self, venues):
        venues.get_wlans("v-1")
        data = venues.client.post.call_args[1]["data"]
        assert data == {}

    def test_kwargs_sent_as_data(self, venues):
        venues.get_wlans("v-1", searchString="guest")
        data = venues.client.post.call_args[1]["data"]
        assert data == {"searchString": "guest"}

    def test_returns_wlan_data(self, venues):
        expected = {"data": [{"ssid": "Corp-WiFi"}]}
        venues.client.post.return_value = expected
        assert venues.get_wlans("v-1") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-v not found"):
            venues.get_wlans("bad-v")

    def test_404_preserves_status_code(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.get_wlans("bad-v")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.post.side_effect = OSError("network down")
        with pytest.raises(OSError, match="network down"):
            venues.get_wlans("v-1")


# ── get_clients ─────────────────────────────────────────────────────────────


class TestGetClients:
    """Tests for Venues.get_clients()."""

    def test_posts_to_correct_endpoint(self, venues):
        venues.get_clients("v-1")
        venues.client.post.assert_called_once()
        args, _ = venues.client.post.call_args
        assert args[0] == "/venues/v-1/clients/query"

    def test_empty_kwargs_sends_empty_dict(self, venues):
        venues.get_clients("v-1")
        data = venues.client.post.call_args[1]["data"]
        assert data == {}

    def test_kwargs_sent_as_data(self, venues):
        venues.get_clients("v-1", pageSize=25, sortOrder="DESC")
        data = venues.client.post.call_args[1]["data"]
        assert data == {"pageSize": 25, "sortOrder": "DESC"}

    def test_returns_client_data(self, venues):
        expected = {"data": [{"mac": "AA:BB:CC:DD:EE:FF"}], "totalCount": 1}
        venues.client.post.return_value = expected
        assert venues.get_clients("v-1") == expected

    def test_404_raises_resource_not_found_with_message(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-v not found"):
            venues.get_clients("bad-v")

    def test_404_preserves_status_code(self, venues):
        venues.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            venues.get_clients("bad-v")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, venues):
        venues.client.post.side_effect = IOError("disk full")
        with pytest.raises(IOError, match="disk full"):
            venues.get_clients("v-1")


# ── constructor ─────────────────────────────────────────────────────────────


class TestConstructor:
    """Tests for Venues.__init__."""

    def test_stores_client_reference(self):
        client = MagicMock()
        v = Venues(client)
        assert v.client is client
