"""Unit tests for the APs module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.aps import APs


@pytest.fixture
def aps(mock_client):
    """Create an APs instance backed by a mock client."""
    return APs(mock_client)


# ── list ─────────────────────────────────────────────────────────────────────


class TestList:
    """Tests for APs.list()."""

    def test_default_query(self, aps):
        """list() with no args should POST default pagination to /venues/aps/query."""
        aps.client.post.return_value = {"data": [], "totalCount": 0}

        result = aps.list()

        aps.client.post.assert_called_once_with(
            "/venues/aps/query",
            data={"pageSize": 100, "page": 0, "sortOrder": "ASC"},
        )
        assert result == {"data": [], "totalCount": 0}

    def test_custom_query(self, aps):
        """list() should forward custom query_data as-is."""
        custom_query = {
            "filters": [{"type": "VENUE", "value": "v-123"}],
            "pageSize": 50,
            "page": 2,
            "sortOrder": "DESC",
        }
        aps.client.post.return_value = {"data": [{"id": "ap-1"}], "totalCount": 1}

        result = aps.list(query_data=custom_query)

        aps.client.post.assert_called_once_with("/venues/aps/query", data=custom_query)
        assert result["totalCount"] == 1

    def test_sort_order_uppercased(self, aps):
        """list() should uppercase the sortOrder value."""
        query = {"sortOrder": "desc", "pageSize": 10, "page": 0}
        aps.client.post.return_value = {"data": []}

        aps.list(query_data=query)

        called_data = aps.client.post.call_args[1]["data"]
        assert called_data["sortOrder"] == "DESC"

    def test_propagates_exception(self, aps):
        """list() should let unexpected exceptions bubble up."""
        aps.client.post.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            aps.list()

    def test_returns_post_result(self, aps):
        """list() should return exactly what client.post returns."""
        expected = {"data": [{"id": "a"}, {"id": "b"}], "totalCount": 2}
        aps.client.post.return_value = expected

        assert aps.list() is expected


# ── get ──────────────────────────────────────────────────────────────────────


class TestGet:
    """Tests for APs.get()."""

    def test_posts_id_filter(self, aps):
        """get() should POST a query with an ID filter."""
        ap_data = {"id": "ap-42", "name": "Lobby AP"}
        aps.client.post.return_value = {"data": [ap_data]}

        result = aps.get("ap-42")

        aps.client.post.assert_called_once_with(
            "/venues/aps/query",
            data={"filters": [{"type": "ID", "value": "ap-42"}]},
        )
        assert result == ap_data

    def test_returns_first_item(self, aps):
        """get() should return only the first item from the data list."""
        aps.client.post.return_value = {
            "data": [{"id": "ap-1"}, {"id": "ap-2"}]
        }

        result = aps.get("ap-1")

        assert result == {"id": "ap-1"}

    def test_not_found_empty_data(self, aps):
        """get() should raise ResourceNotFoundError when data list is empty."""
        aps.client.post.return_value = {"data": []}

        with pytest.raises(ResourceNotFoundError, match="AP with ID ap-999 not found"):
            aps.get("ap-999")

    def test_not_found_no_data_key(self, aps):
        """get() should raise ResourceNotFoundError when 'data' key is missing."""
        aps.client.post.return_value = {}

        with pytest.raises(ResourceNotFoundError):
            aps.get("ap-missing")

    def test_re_raises_resource_not_found(self, aps):
        """get() should re-raise ResourceNotFoundError from the client as its own."""
        aps.client.post.side_effect = ResourceNotFoundError(message="server 404")

        with pytest.raises(ResourceNotFoundError, match="AP with ID ap-x not found"):
            aps.get("ap-x")

    def test_propagates_other_exception(self, aps):
        """get() should let non-ResourceNotFoundError exceptions bubble up."""
        aps.client.post.side_effect = ConnectionError("timeout")

        with pytest.raises(ConnectionError, match="timeout"):
            aps.get("ap-1")


# ── update ───────────────────────────────────────────────────────────────────


class TestUpdate:
    """Tests for APs.update()."""

    def test_puts_with_kwargs(self, aps):
        """update() should PUT kwargs to the correct endpoint."""
        aps.client.put.return_value = {"id": "ap-1", "name": "New Name"}

        result = aps.update("v-1", "SN-001", name="New Name", description="Updated")

        aps.client.put.assert_called_once_with(
            "/venues/v-1/aps/SN-001",
            data={"name": "New Name", "description": "Updated"},
        )
        assert result["name"] == "New Name"

    def test_empty_kwargs(self, aps):
        """update() with no kwargs should PUT an empty dict."""
        aps.client.put.return_value = {}

        aps.update("v-1", "SN-001")

        aps.client.put.assert_called_once_with("/venues/v-1/aps/SN-001", data={})

    def test_not_found(self, aps):
        """update() should raise ResourceNotFoundError when the AP is missing."""
        aps.client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.update("v-1", "SN-001", name="x")

    def test_returns_put_result(self, aps):
        """update() should return whatever client.put returns."""
        expected = {"status": "ok"}
        aps.client.put.return_value = expected

        assert aps.update("v-1", "SN-001") is expected


# ── reboot ───────────────────────────────────────────────────────────────────


class TestReboot:
    """Tests for APs.reboot()."""

    def test_patches_system_commands(self, aps):
        """reboot() should PATCH the systemCommands endpoint with REBOOT type."""
        aps.client.patch.return_value = {"status": "rebooting"}

        result = aps.reboot("v-1", "SN-001")

        aps.client.patch.assert_called_once_with(
            "/venues/v-1/aps/SN-001/systemCommands",
            data={"type": "REBOOT"},
        )
        assert result == {"status": "rebooting"}

    def test_not_found(self, aps):
        """reboot() should raise ResourceNotFoundError for a missing AP."""
        aps.client.patch.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-002 not found in venue v-1"):
            aps.reboot("v-1", "SN-002")

    def test_returns_patch_result(self, aps):
        """reboot() should return whatever client.patch returns."""
        expected = {"taskId": "t-123"}
        aps.client.patch.return_value = expected

        assert aps.reboot("v-1", "SN-001") is expected


# ── get_clients ──────────────────────────────────────────────────────────────


class TestGetClients:
    """Tests for APs.get_clients()."""

    def test_without_serial_number(self, aps):
        """get_clients() without serial_number should POST with only kwargs."""
        aps.client.post.return_value = {"data": [], "totalCount": 0}

        result = aps.get_clients("v-1", pageSize=50)

        aps.client.post.assert_called_once_with(
            "/venues/aps/clients/query",
            data={"pageSize": 50},
        )
        assert result["totalCount"] == 0

    def test_with_serial_number(self, aps):
        """get_clients() with serial_number should add it to filters."""
        aps.client.post.return_value = {"data": [{"mac": "aa:bb:cc:dd:ee:ff"}]}

        result = aps.get_clients("v-1", serial_number="SN-001", pageSize=10)

        called_data = aps.client.post.call_args[1]["data"]
        assert called_data["filters"]["serialNumber"] == "SN-001"
        assert called_data["pageSize"] == 10

    def test_serial_number_preserves_existing_filters(self, aps):
        """get_clients() should merge serialNumber into existing filters dict."""
        aps.client.post.return_value = {"data": []}

        aps.get_clients("v-1", serial_number="SN-001", filters={"status": "ONLINE"})

        called_data = aps.client.post.call_args[1]["data"]
        assert called_data["filters"]["serialNumber"] == "SN-001"
        assert called_data["filters"]["status"] == "ONLINE"

    def test_no_kwargs_no_serial(self, aps):
        """get_clients() with only venue_id should POST an empty dict."""
        aps.client.post.return_value = {"data": []}

        aps.get_clients("v-1")

        aps.client.post.assert_called_once_with(
            "/venues/aps/clients/query",
            data={},
        )

    def test_not_found_with_serial(self, aps):
        """get_clients() should mention serial number in error when provided."""
        aps.client.post.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.get_clients("v-1", serial_number="SN-001")

    def test_not_found_without_serial(self, aps):
        """get_clients() should mention venue in error when no serial number."""
        aps.client.post.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v-1 not found"):
            aps.get_clients("v-1")


# ── get_radio_settings ───────────────────────────────────────────────────────


class TestGetRadioSettings:
    """Tests for APs.get_radio_settings()."""

    def test_gets_correct_endpoint(self, aps):
        """get_radio_settings() should GET the radioSettings endpoint."""
        expected = {"radio24g": {"channel": 6}, "radio5g": {"channel": 36}}
        aps.client.get.return_value = expected

        result = aps.get_radio_settings("v-1", "SN-001")

        aps.client.get.assert_called_once_with(
            "/venues/v-1/aps/SN-001/radioSettings"
        )
        assert result == expected

    def test_not_found(self, aps):
        """get_radio_settings() should raise ResourceNotFoundError for missing AP."""
        aps.client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.get_radio_settings("v-1", "SN-001")


# ── update_radio_settings ───────────────────────────────────────────────────


class TestUpdateRadioSettings:
    """Tests for APs.update_radio_settings()."""

    def test_puts_settings(self, aps):
        """update_radio_settings() should PUT settings to the radioSettings endpoint."""
        settings = {"radio24g": {"channel": 11, "txPower": "auto"}}
        aps.client.put.return_value = settings

        result = aps.update_radio_settings("v-1", "SN-001", settings)

        aps.client.put.assert_called_once_with(
            "/venues/v-1/aps/SN-001/radioSettings",
            data=settings,
        )
        assert result == settings

    def test_not_found(self, aps):
        """update_radio_settings() should raise ResourceNotFoundError for missing AP."""
        aps.client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.update_radio_settings("v-1", "SN-001", {})

    def test_returns_put_result(self, aps):
        """update_radio_settings() should return whatever client.put returns."""
        expected = {"updated": True}
        aps.client.put.return_value = expected

        assert aps.update_radio_settings("v-1", "SN-001", {"channel": 1}) is expected


# ── get_statistics ───────────────────────────────────────────────────────────


class TestGetStatistics:
    """Tests for APs.get_statistics()."""

    def test_gets_correct_endpoint(self, aps):
        """get_statistics() should GET the statistics endpoint."""
        expected = {"uptime": 86400, "clients": 15}
        aps.client.get.return_value = expected

        result = aps.get_statistics("v-1", "SN-001")

        aps.client.get.assert_called_once_with(
            "/venues/v-1/aps/SN-001/statistics"
        )
        assert result == expected

    def test_not_found(self, aps):
        """get_statistics() should raise ResourceNotFoundError for missing AP."""
        aps.client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.get_statistics("v-1", "SN-001")


# ── add_to_group ─────────────────────────────────────────────────────────────


class TestAddToGroup:
    """Tests for APs.add_to_group()."""

    def test_posts_serial_numbers(self, aps):
        """add_to_group() should POST serial numbers to the members endpoint."""
        serials = ["SN-001", "SN-002", "SN-003"]
        aps.client.post.return_value = {"added": 3}

        result = aps.add_to_group("v-1", "grp-1", serials)

        aps.client.post.assert_called_once_with(
            "/venues/v-1/apGroups/grp-1/members",
            data={"serialNumbers": serials},
        )
        assert result == {"added": 3}

    def test_single_serial(self, aps):
        """add_to_group() should work with a single-item list."""
        aps.client.post.return_value = {"added": 1}

        aps.add_to_group("v-1", "grp-1", ["SN-001"])

        called_data = aps.client.post.call_args[1]["data"]
        assert called_data["serialNumbers"] == ["SN-001"]

    def test_not_found_group(self, aps):
        """add_to_group() should mention 'group' when the error mentions group."""
        aps.client.post.side_effect = ResourceNotFoundError(
            message="AP group not found"
        )

        with pytest.raises(ResourceNotFoundError, match="AP group with ID grp-1 not found"):
            aps.add_to_group("v-1", "grp-1", ["SN-001"])

    def test_not_found_venue(self, aps):
        """add_to_group() should mention venue when error does not mention group."""
        aps.client.post.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v-1 not found"):
            aps.add_to_group("v-1", "grp-1", ["SN-001"])


# ── get_venue_ap_management_vlan ─────────────────────────────────────────────


class TestGetVenueApManagementVlan:
    """Tests for APs.get_venue_ap_management_vlan()."""

    def test_gets_correct_endpoint(self, aps):
        """Should GET the venue-level management VLAN settings."""
        expected = {"vlanId": 100, "enabled": True}
        aps.client.get.return_value = expected

        result = aps.get_venue_ap_management_vlan("v-1")

        aps.client.get.assert_called_once_with(
            "/venues/v-1/apManagementTrafficVlanSettings"
        )
        assert result == expected

    def test_not_found(self, aps):
        """Should raise ResourceNotFoundError for a missing venue."""
        aps.client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v-1 not found"):
            aps.get_venue_ap_management_vlan("v-1")


# ── update_venue_ap_management_vlan ──────────────────────────────────────────


class TestUpdateVenueApManagementVlan:
    """Tests for APs.update_venue_ap_management_vlan()."""

    def test_puts_kwargs(self, aps):
        """Should PUT kwargs to the venue-level management VLAN endpoint."""
        aps.client.put.return_value = {"vlanId": 200, "enabled": True}

        result = aps.update_venue_ap_management_vlan("v-1", vlanId=200, enabled=True)

        aps.client.put.assert_called_once_with(
            "/venues/v-1/apManagementTrafficVlanSettings",
            data={"vlanId": 200, "enabled": True},
        )
        assert result["vlanId"] == 200

    def test_empty_kwargs(self, aps):
        """Should PUT an empty dict when no kwargs are given."""
        aps.client.put.return_value = {}

        aps.update_venue_ap_management_vlan("v-1")

        aps.client.put.assert_called_once_with(
            "/venues/v-1/apManagementTrafficVlanSettings",
            data={},
        )

    def test_not_found(self, aps):
        """Should raise ResourceNotFoundError for a missing venue."""
        aps.client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v-1 not found"):
            aps.update_venue_ap_management_vlan("v-1", vlanId=100)


# ── get_ap_management_vlan ───────────────────────────────────────────────────


class TestGetApManagementVlan:
    """Tests for APs.get_ap_management_vlan()."""

    def test_gets_correct_endpoint(self, aps):
        """Should GET the AP-level management VLAN settings."""
        expected = {"vlanId": 50, "mode": "CUSTOM"}
        aps.client.get.return_value = expected

        result = aps.get_ap_management_vlan("v-1", "SN-001")

        aps.client.get.assert_called_once_with(
            "/venues/v-1/aps/SN-001/managementTrafficVlanSettings"
        )
        assert result == expected

    def test_not_found(self, aps):
        """Should raise ResourceNotFoundError for a missing AP."""
        aps.client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.get_ap_management_vlan("v-1", "SN-001")


# ── update_ap_management_vlan ────────────────────────────────────────────────


class TestUpdateApManagementVlan:
    """Tests for APs.update_ap_management_vlan()."""

    def test_puts_kwargs(self, aps):
        """Should PUT kwargs to the AP-level management VLAN endpoint."""
        aps.client.put.return_value = {"vlanId": 75, "mode": "CUSTOM"}

        result = aps.update_ap_management_vlan("v-1", "SN-001", vlanId=75, mode="CUSTOM")

        aps.client.put.assert_called_once_with(
            "/venues/v-1/aps/SN-001/managementTrafficVlanSettings",
            data={"vlanId": 75, "mode": "CUSTOM"},
        )
        assert result["vlanId"] == 75

    def test_empty_kwargs(self, aps):
        """Should PUT an empty dict when no kwargs are given."""
        aps.client.put.return_value = {}

        aps.update_ap_management_vlan("v-1", "SN-001")

        aps.client.put.assert_called_once_with(
            "/venues/v-1/aps/SN-001/managementTrafficVlanSettings",
            data={},
        )

    def test_not_found(self, aps):
        """Should raise ResourceNotFoundError for a missing AP."""
        aps.client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match="SN-001 not found in venue v-1"):
            aps.update_ap_management_vlan("v-1", "SN-001", vlanId=100)

    def test_returns_put_result(self, aps):
        """Should return whatever client.put returns."""
        expected = {"updated": True}
        aps.client.put.return_value = expected

        assert aps.update_ap_management_vlan("v-1", "SN-001", vlanId=1) is expected
