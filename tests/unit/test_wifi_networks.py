"""Comprehensive unit tests for the WiFiNetworks module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.wifi_networks import WiFiNetworks


@pytest.fixture
def wifi():
    """Create a WiFiNetworks instance backed by a mock client."""
    client = MagicMock()
    return WiFiNetworks(client)


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------

class TestList:
    """Tests for WiFiNetworks.list()."""

    def test_list_default_query(self, wifi):
        """list() with no args should POST default pagination body."""
        wifi.client.post.return_value = {"data": [], "totalCount": 0}

        result = wifi.list()

        wifi.client.post.assert_called_once_with(
            "/wifiNetworks/query",
            data={"pageSize": 100, "page": 0, "sortOrder": "ASC"},
        )
        assert result == {"data": [], "totalCount": 0}

    def test_list_custom_query(self, wifi):
        """list() should forward custom query_data to the API."""
        query = {"pageSize": 50, "page": 2, "sortOrder": "desc", "filters": {"name": "Guest"}}
        wifi.client.post.return_value = {"data": [{"id": "w1"}], "totalCount": 1}

        result = wifi.list(query_data=query)

        # sortOrder should be uppercased
        expected = {**query, "sortOrder": "DESC"}
        wifi.client.post.assert_called_once_with("/wifiNetworks/query", data=expected)
        assert result["totalCount"] == 1

    def test_list_sort_order_uppercased(self, wifi):
        """list() should uppercase the sortOrder value."""
        wifi.client.post.return_value = {}
        wifi.list(query_data={"sortOrder": "asc", "pageSize": 10, "page": 0})

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["sortOrder"] == "ASC"

    def test_list_no_sort_order_key(self, wifi):
        """list() should not crash when query_data lacks sortOrder."""
        wifi.client.post.return_value = {}
        wifi.list(query_data={"pageSize": 10, "page": 0})

        called_data = wifi.client.post.call_args[1]["data"]
        assert "sortOrder" not in called_data

    def test_list_propagates_exception(self, wifi):
        """list() should re-raise exceptions from the client."""
        wifi.client.post.side_effect = RuntimeError("connection lost")

        with pytest.raises(RuntimeError, match="connection lost"):
            wifi.list()


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    """Tests for WiFiNetworks.get()."""

    def test_get_success(self, wifi):
        """get() should GET /wifiNetworks/{id} and return the result."""
        wifi.client.get.return_value = {"id": "abc", "name": "Corp"}

        result = wifi.get("abc")

        wifi.client.get.assert_called_once_with("/wifiNetworks/abc")
        assert result["name"] == "Corp"

    def test_get_not_found(self, wifi):
        """get() should raise ResourceNotFoundError with descriptive message on 404."""
        wifi.client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="WLAN with ID xyz not found"):
            wifi.get("xyz")

    def test_get_other_exception_propagates(self, wifi):
        """get() should not catch non-ResourceNotFoundError exceptions."""
        wifi.client.get.side_effect = RuntimeError("server error")

        with pytest.raises(RuntimeError):
            wifi.get("abc")


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestCreate:
    """Tests for WiFiNetworks.create()."""

    def test_create_open_network(self, wifi):
        """create() for an open network should build correct nested payload."""
        wifi.client.post.return_value = {"id": "new-id"}

        result = wifi.create(name="Guest", ssid="Guest-WiFi", security_type="open")

        wifi.client.post.assert_called_once_with(
            "/wifiNetworks",
            data={
                "type": "open",
                "name": "Guest",
                "wlan": {
                    "ssid": "Guest-WiFi",
                    "wlanSecurity": "Open",
                    "enabled": True,
                },
            },
        )
        assert result["id"] == "new-id"

    def test_create_psk_network(self, wifi):
        """create() for a PSK network should include passphrase in wlan."""
        wifi.client.post.return_value = {"id": "w2"}

        wifi.create(
            name="Corp",
            ssid="Corp-WiFi",
            security_type="wpa2-psk",
            passphrase="secret123",
        )

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["type"] == "psk"
        assert called_data["wlan"]["wlanSecurity"] == "WPA2Personal"
        assert called_data["wlan"]["passphrase"] == "secret123"

    def test_create_psk_requires_passphrase(self, wifi):
        """create() should raise ValueError when passphrase missing for PSK."""
        with pytest.raises(ValueError, match="passphrase is required"):
            wifi.create(name="X", ssid="X", security_type="psk")

    def test_create_psk_default_security_type(self, wifi):
        """create() defaults to 'psk' security_type."""
        with pytest.raises(ValueError, match="passphrase is required"):
            wifi.create(name="X", ssid="X")

    def test_create_unknown_security_type(self, wifi):
        """create() should raise ValueError for unknown security types."""
        with pytest.raises(ValueError, match="Unknown security_type"):
            wifi.create(name="X", ssid="X", security_type="wep")

    def test_create_aaa_network(self, wifi):
        """create() for enterprise should set AAAWifiNetwork type."""
        wifi.client.post.return_value = {"id": "w3"}

        wifi.create(name="Ent", ssid="Ent-WiFi", security_type="wpa2-enterprise")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["type"] == "aaa"
        assert called_data["wlan"]["wlanSecurity"] == "WPA2Enterprise"
        assert "passphrase" not in called_data["wlan"]

    def test_create_hidden_network(self, wifi):
        """create() with hidden=True should set advancedCustomization.hideSsid."""
        wifi.client.post.return_value = {}

        wifi.create(name="X", ssid="X", security_type="open", hidden=True)

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["wlan"]["advancedCustomization"]["hideSsid"] is True

    def test_create_vlan_id_in_wlan(self, wifi):
        """create() should nest vlan_id inside wlan, not at top level."""
        wifi.client.post.return_value = {}

        wifi.create(name="X", ssid="X", security_type="open", vlan_id=100)

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["wlan"]["vlanId"] == 100
        assert "vlanId" not in called_data

    def test_create_vlan_id_none_excluded(self, wifi):
        """create() should not include vlanId when vlan_id is None."""
        wifi.client.post.return_value = {}
        wifi.create(name="X", ssid="X", security_type="open")

        called_data = wifi.client.post.call_args[1]["data"]
        assert "vlanId" not in called_data["wlan"]

    def test_create_with_description(self, wifi):
        """create() should include description at top level when provided."""
        wifi.client.post.return_value = {}

        wifi.create(name="X", ssid="X", security_type="open", description="Test net")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["description"] == "Test net"

    def test_create_empty_description_excluded(self, wifi):
        """create() should not include description when it is falsy."""
        wifi.client.post.return_value = {}
        wifi.create(name="X", ssid="X", security_type="open", description="")

        called_data = wifi.client.post.call_args[1]["data"]
        assert "description" not in called_data

    def test_create_open_no_passphrase_in_payload(self, wifi):
        """create() for open network should not include passphrase."""
        wifi.client.post.return_value = {}
        wifi.create(name="X", ssid="X", security_type="open")

        called_data = wifi.client.post.call_args[1]["data"]
        assert "passphrase" not in called_data["wlan"]

    def test_create_with_kwargs(self, wifi):
        """create() should merge extra **kwargs at top level."""
        wifi.client.post.return_value = {}

        wifi.create(name="X", ssid="X", security_type="open", customField="val")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["customField"] == "val"

    def test_create_with_wlan_options(self, wifi):
        """create() should merge wlan_options into the wlan object."""
        wifi.client.post.return_value = {}

        wifi.create(
            name="X", ssid="X", security_type="open",
            wlan_options={"bandBalancing": True},
        )

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["wlan"]["bandBalancing"] is True

    def test_create_with_advanced_options(self, wifi):
        """create() should merge advanced_options into advancedCustomization."""
        wifi.client.post.return_value = {}

        wifi.create(
            name="X", ssid="X", security_type="open",
            advanced_options={"maxClients": 50},
        )

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["wlan"]["advancedCustomization"]["maxClients"] == 50

    def test_create_wpa3_psk(self, wifi):
        """create() with wpa3-psk should set correct type and security."""
        wifi.client.post.return_value = {}

        wifi.create(name="X", ssid="X", security_type="wpa3-psk", passphrase="12345678")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["type"] == "psk"
        assert called_data["wlan"]["wlanSecurity"] == "WPA3"


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUpdate:
    """Tests for WiFiNetworks.update()."""

    def test_update_success(self, wifi):
        """update() should PUT kwargs to /wifiNetworks/{id}."""
        wifi.client.put.return_value = {"id": "w1", "name": "Renamed"}

        result = wifi.update("w1", name="Renamed", hidden=True)

        wifi.client.put.assert_called_once_with(
            "/wifiNetworks/w1",
            data={"name": "Renamed", "hidden": True},
        )
        assert result["name"] == "Renamed"

    def test_update_not_found(self, wifi):
        """update() should raise ResourceNotFoundError with descriptive message."""
        wifi.client.put.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="WLAN with ID gone not found"):
            wifi.update("gone", name="Nope")

    def test_update_no_kwargs(self, wifi):
        """update() with no kwargs should PUT an empty dict."""
        wifi.client.put.return_value = {}
        wifi.update("w1")

        wifi.client.put.assert_called_once_with("/wifiNetworks/w1", data={})


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    """Tests for WiFiNetworks.delete()."""

    def test_delete_success(self, wifi):
        """delete() should call client.delete on the correct path."""
        wifi.delete("w1")

        wifi.client.delete.assert_called_once_with("/wifiNetworks/w1")

    def test_delete_returns_none(self, wifi):
        """delete() should return None on success."""
        result = wifi.delete("w1")
        assert result is None

    def test_delete_not_found(self, wifi):
        """delete() should raise ResourceNotFoundError with descriptive message."""
        wifi.client.delete.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="WLAN with ID w99 not found"):
            wifi.delete("w99")


# ---------------------------------------------------------------------------
# list_venue_wlans()
# ---------------------------------------------------------------------------

class TestListVenueWlans:
    """Tests for WiFiNetworks.list_venue_wlans()."""

    def test_list_venue_wlans_default(self, wifi):
        """list_venue_wlans() should POST with venueId filter and defaults."""
        wifi.client.post.return_value = {"data": []}

        wifi.list_venue_wlans("v1")

        wifi.client.post.assert_called_once_with(
            "/venues/wifiNetworks/query",
            data={
                "pageSize": 100,
                "page": 0,
                "filters": {"venueId": "v1"},
            },
        )

    def test_list_venue_wlans_with_search(self, wifi):
        """list_venue_wlans() should include searchString when provided."""
        wifi.client.post.return_value = {"data": []}

        wifi.list_venue_wlans("v1", search_string="Guest")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["searchString"] == "Guest"
        assert called_data["filters"]["venueId"] == "v1"

    def test_list_venue_wlans_custom_pagination(self, wifi):
        """list_venue_wlans() should respect page_size and page params."""
        wifi.client.post.return_value = {"data": []}

        wifi.list_venue_wlans("v1", page_size=25, page=3)

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["pageSize"] == 25
        assert called_data["page"] == 3

    def test_list_venue_wlans_extra_kwargs_become_filters(self, wifi):
        """list_venue_wlans() should merge extra kwargs into filters."""
        wifi.client.post.return_value = {"data": []}

        wifi.list_venue_wlans("v1", status="active")

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["filters"]["status"] == "active"
        assert called_data["filters"]["venueId"] == "v1"

    def test_list_venue_wlans_explicit_filters_kwarg(self, wifi):
        """list_venue_wlans() should merge an explicit filters dict."""
        wifi.client.post.return_value = {"data": []}

        wifi.list_venue_wlans("v1", filters={"securityType": "wpa2-psk"})

        called_data = wifi.client.post.call_args[1]["data"]
        assert called_data["filters"]["venueId"] == "v1"
        assert called_data["filters"]["securityType"] == "wpa2-psk"

    def test_list_venue_wlans_not_found(self, wifi):
        """list_venue_wlans() should raise ResourceNotFoundError for missing venue."""
        wifi.client.post.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v99 not found"):
            wifi.list_venue_wlans("v99")


# ---------------------------------------------------------------------------
# deploy_to_venue()
# ---------------------------------------------------------------------------

class TestDeployToVenue:
    """Tests for WiFiNetworks.deploy_to_venue()."""

    def test_deploy_default(self, wifi):
        """deploy_to_venue() should PUT isAllApGroups to the correct endpoint."""
        wifi.client.put.return_value = {"status": "deployed"}

        result = wifi.deploy_to_venue("w1", "v1")

        wifi.client.put.assert_called_once_with(
            "/venues/v1/wifiNetworks/w1",
            data={"isAllApGroups": True},
        )
        assert result["status"] == "deployed"

    def test_deploy_specific_ap_groups(self, wifi):
        """deploy_to_venue() should allow disabling isAllApGroups."""
        wifi.client.put.return_value = {}

        wifi.deploy_to_venue("w1", "v1", is_all_ap_groups=False)

        called_data = wifi.client.put.call_args[1]["data"]
        assert called_data["isAllApGroups"] is False

    def test_deploy_with_extra_kwargs(self, wifi):
        """deploy_to_venue() should merge additional kwargs into the payload."""
        wifi.client.put.return_value = {}

        wifi.deploy_to_venue("w1", "v1", priority=5)

        called_data = wifi.client.put.call_args[1]["data"]
        assert called_data["priority"] == 5
        assert called_data["isAllApGroups"] is True

    def test_deploy_wlan_not_found(self, wifi):
        """deploy_to_venue() should raise with WLAN message when error mentions network."""
        wifi.client.put.side_effect = ResourceNotFoundError(message="network not found")

        with pytest.raises(ResourceNotFoundError, match="WLAN with ID w1 not found"):
            wifi.deploy_to_venue("w1", "v1")

    def test_deploy_venue_not_found(self, wifi):
        """deploy_to_venue() should raise with Venue message for non-network errors."""
        wifi.client.put.side_effect = ResourceNotFoundError(message="venue missing")

        with pytest.raises(ResourceNotFoundError, match="Venue with ID v1 not found"):
            wifi.deploy_to_venue("w1", "v1")


# ---------------------------------------------------------------------------
# undeploy_from_venue()
# ---------------------------------------------------------------------------

class TestUndeployFromVenue:
    """Tests for WiFiNetworks.undeploy_from_venue()."""

    def test_undeploy_success(self, wifi):
        """undeploy_from_venue() should DELETE the correct URL."""
        wifi.undeploy_from_venue("w1", "v1")

        wifi.client.delete.assert_called_once_with("/venues/v1/wifiNetworks/w1")

    def test_undeploy_returns_none(self, wifi):
        """undeploy_from_venue() should return None on success."""
        result = wifi.undeploy_from_venue("w1", "v1")
        assert result is None

    def test_undeploy_not_found(self, wifi):
        """undeploy_from_venue() should raise with descriptive message on 404."""
        wifi.client.delete.side_effect = ResourceNotFoundError()

        with pytest.raises(
            ResourceNotFoundError,
            match="WLAN with ID w1 not deployed in venue v1",
        ):
            wifi.undeploy_from_venue("w1", "v1")


# ---------------------------------------------------------------------------
# get_venue_wlan_settings()
# ---------------------------------------------------------------------------

class TestGetVenueWlanSettings:
    """Tests for WiFiNetworks.get_venue_wlan_settings()."""

    def test_get_settings_success(self, wifi):
        """get_venue_wlan_settings() should GET the correct URL."""
        wifi.client.get.return_value = {"vlanId": 100}

        result = wifi.get_venue_wlan_settings("w1", "v1")

        wifi.client.get.assert_called_once_with(
            "/venues/v1/wifiNetworks/w1/settings"
        )
        assert result["vlanId"] == 100

    def test_get_settings_not_found(self, wifi):
        """get_venue_wlan_settings() should raise with descriptive message on 404."""
        wifi.client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(
            ResourceNotFoundError,
            match="WLAN with ID w1 not deployed in venue v1",
        ):
            wifi.get_venue_wlan_settings("w1", "v1")


# ---------------------------------------------------------------------------
# update_venue_wlan_settings()
# ---------------------------------------------------------------------------

class TestUpdateVenueWlanSettings:
    """Tests for WiFiNetworks.update_venue_wlan_settings()."""

    def test_update_settings_success(self, wifi):
        """update_venue_wlan_settings() should PUT kwargs to the correct URL."""
        wifi.client.put.return_value = {"vlanId": 200}

        result = wifi.update_venue_wlan_settings("w1", "v1", vlanId=200)

        wifi.client.put.assert_called_once_with(
            "/venues/v1/wifiNetworks/w1/settings",
            data={"vlanId": 200},
        )
        assert result["vlanId"] == 200

    def test_update_settings_not_found(self, wifi):
        """update_venue_wlan_settings() should raise with descriptive message on 404."""
        wifi.client.put.side_effect = ResourceNotFoundError()

        with pytest.raises(
            ResourceNotFoundError,
            match="WLAN with ID w1 not deployed in venue v1",
        ):
            wifi.update_venue_wlan_settings("w1", "v1", name="X")

    def test_update_settings_no_kwargs(self, wifi):
        """update_venue_wlan_settings() with no kwargs should PUT empty dict."""
        wifi.client.put.return_value = {}
        wifi.update_venue_wlan_settings("w1", "v1")

        wifi.client.put.assert_called_once_with(
            "/venues/v1/wifiNetworks/w1/settings", data={}
        )


# ---------------------------------------------------------------------------
# associate_dpsk_service()
# ---------------------------------------------------------------------------

class TestAssociateDpskService:
    """Tests for WiFiNetworks.associate_dpsk_service()."""

    def test_associate_success(self, wifi):
        """associate_dpsk_service() should PUT empty dict to the correct path."""
        wifi.client.put.return_value = {"status": "ok"}

        result = wifi.associate_dpsk_service("w1", "dpsk1")

        wifi.client.put.assert_called_once_with(
            "/wifiNetworks/w1/dpskServices/dpsk1",
            {},
        )
        assert result["status"] == "ok"

    def test_associate_returns_response(self, wifi):
        """associate_dpsk_service() should return the API response."""
        wifi.client.put.return_value = {"wlanId": "w1", "dpskServiceId": "dpsk1"}

        result = wifi.associate_dpsk_service("w1", "dpsk1")

        assert result["wlanId"] == "w1"
        assert result["dpskServiceId"] == "dpsk1"

    def test_associate_propagates_exception(self, wifi):
        """associate_dpsk_service() should not swallow exceptions."""
        wifi.client.put.side_effect = RuntimeError("server down")

        with pytest.raises(RuntimeError, match="server down"):
            wifi.associate_dpsk_service("w1", "dpsk1")


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

class TestConstructor:
    """Tests for WiFiNetworks.__init__()."""

    def test_stores_client_reference(self):
        """WiFiNetworks should store the client reference."""
        client = MagicMock()
        wn = WiFiNetworks(client)
        assert wn.client is client


# ── list_all ─────────────────────────────────────────────────────────────


class TestListAll:
    """Tests for WiFiNetworks.list_all()."""

    def test_delegates_to_paginate_query(self, wifi):
        wifi.client.paginate_query.return_value = [{"id": "wn1"}]
        result = wifi.list_all()
        wifi.client.paginate_query.assert_called_once_with("/wifiNetworks/query", None)
        assert result == [{"id": "wn1"}]

    def test_passes_query_data(self, wifi):
        wifi.client.paginate_query.return_value = []
        q = {"filters": [{"type": "VENUE", "value": "v1"}]}
        wifi.list_all(query_data=q)
        wifi.client.paginate_query.assert_called_once_with("/wifiNetworks/query", q)
