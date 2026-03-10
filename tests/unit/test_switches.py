"""Comprehensive unit tests for the Switches module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.modules.switches import Switches
from r1_sdk.exceptions import ResourceNotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a mock R1Client."""
    return MagicMock()


@pytest.fixture
def switches(client):
    """Create a Switches instance backed by a mock client."""
    return Switches(client)


# IDs reused across tests
VENUE_ID = "venue-001"
SWITCH_ID = "switch-abc"
PORT_ID = "port-42"
VLAN_ID = 100


# =========================================================================
# list()
# =========================================================================

class TestList:
    """Tests for Switches.list()."""

    def test_default_query(self, switches, client):
        """list() with no args should POST default pagination body."""
        client.post.return_value = {"data": [], "totalCount": 0}

        result = switches.list()

        client.post.assert_called_once_with(
            "/venues/switches/query",
            data={"pageSize": 100, "page": 0, "sortOrder": "ASC"},
        )
        assert result == {"data": [], "totalCount": 0}

    def test_custom_query(self, switches, client):
        """list() should forward custom query data."""
        query = {
            "filters": [{"type": "VENUE", "value": VENUE_ID}],
            "pageSize": 50,
            "page": 2,
            "sortOrder": "DESC",
        }
        client.post.return_value = {"data": [{"id": "sw1"}], "totalCount": 1}

        result = switches.list(query_data=query)

        client.post.assert_called_once_with(
            "/venues/switches/query",
            data=query,
        )
        assert result["totalCount"] == 1

    def test_sort_order_uppercased(self, switches, client):
        """list() should uppercase the sortOrder value."""
        client.post.return_value = {}

        switches.list(query_data={"sortOrder": "desc", "pageSize": 10, "page": 0})

        posted_data = client.post.call_args[1]["data"] if client.post.call_args[1] else client.post.call_args[0][1]
        # The data dict is mutated in place, so check the value passed
        actual_data = client.post.call_args
        assert actual_data[0][0] == "/venues/switches/query"
        # sortOrder should have been uppercased
        assert actual_data[1]["data"]["sortOrder"] == "DESC" if "data" in actual_data[1] else True

    def test_sort_order_uppercased_positional(self, switches, client):
        """Verify sortOrder uppercasing via the actual call."""
        query = {"sortOrder": "asc", "pageSize": 20, "page": 1}
        client.post.return_value = {}

        switches.list(query_data=query)

        # The query dict is mutated in-place before being passed
        assert query["sortOrder"] == "ASC"

    def test_propagates_exception(self, switches, client):
        """list() should propagate exceptions from client.post."""
        client.post.side_effect = RuntimeError("connection timeout")

        with pytest.raises(RuntimeError, match="connection timeout"):
            switches.list()


# =========================================================================
# get()
# =========================================================================

class TestGet:
    """Tests for Switches.get()."""

    def test_success(self, switches, client):
        """get() should return switch details on success."""
        expected = {"id": SWITCH_ID, "name": "Core Switch"}
        client.get.return_value = expected

        result = switches.get(VENUE_ID, SWITCH_ID)

        client.get.assert_called_once_with(f"/venues/{VENUE_ID}/switches/{SWITCH_ID}")
        assert result == expected

    def test_not_found(self, switches, client):
        """get() should raise ResourceNotFoundError on 404."""
        client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.get(VENUE_ID, SWITCH_ID)

    def test_not_found_includes_venue(self, switches, client):
        """The error message should reference both the switch and venue."""
        client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError) as exc_info:
            switches.get(VENUE_ID, SWITCH_ID)

        assert VENUE_ID in str(exc_info.value)
        assert SWITCH_ID in str(exc_info.value)


# =========================================================================
# update()
# =========================================================================

class TestUpdate:
    """Tests for Switches.update()."""

    def test_success(self, switches, client):
        """update() should PUT kwargs to the correct endpoint."""
        client.put.return_value = {"id": SWITCH_ID, "name": "Renamed"}

        result = switches.update(VENUE_ID, SWITCH_ID, name="Renamed", description="Updated")

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}",
            data={"name": "Renamed", "description": "Updated"},
        )
        assert result["name"] == "Renamed"

    def test_no_kwargs(self, switches, client):
        """update() with no kwargs should PUT an empty dict."""
        client.put.return_value = {}

        switches.update(VENUE_ID, SWITCH_ID)

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}",
            data={},
        )

    def test_not_found(self, switches, client):
        """update() should raise ResourceNotFoundError on 404."""
        client.put.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.update(VENUE_ID, SWITCH_ID, name="X")


# =========================================================================
# reboot()
# =========================================================================

class TestReboot:
    """Tests for Switches.reboot()."""

    def test_success(self, switches, client):
        """reboot() should POST to the reboot endpoint."""
        client.post.return_value = {"status": "rebooting"}

        result = switches.reboot(VENUE_ID, SWITCH_ID)

        client.post.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/reboot"
        )
        assert result["status"] == "rebooting"

    def test_not_found(self, switches, client):
        """reboot() should raise ResourceNotFoundError if switch missing."""
        client.post.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.reboot(VENUE_ID, SWITCH_ID)


# =========================================================================
# get_ports()
# =========================================================================

class TestGetPorts:
    """Tests for Switches.get_ports()."""

    def test_default_query(self, switches, client):
        """get_ports() with no args should POST default pagination body."""
        client.post.return_value = {"data": [], "totalCount": 0}

        result = switches.get_ports()

        client.post.assert_called_once_with(
            "/venues/switches/switchPorts/query",
            data={"pageSize": 100, "page": 0, "sortOrder": "ASC"},
        )
        assert result == {"data": [], "totalCount": 0}

    def test_custom_query(self, switches, client):
        """get_ports() should forward custom query data."""
        query = {
            "filters": [{"type": "SWITCH", "value": SWITCH_ID}],
            "pageSize": 25,
            "page": 0,
        }
        client.post.return_value = {"data": [{"id": "p1"}]}

        result = switches.get_ports(query_data=query)

        client.post.assert_called_once_with(
            "/venues/switches/switchPorts/query",
            data=query,
        )
        assert len(result["data"]) == 1

    def test_sort_order_uppercased(self, switches, client):
        """get_ports() should uppercase sortOrder."""
        query = {"sortOrder": "desc", "pageSize": 10, "page": 0}
        client.post.return_value = {}

        switches.get_ports(query_data=query)

        assert query["sortOrder"] == "DESC"

    def test_no_sort_order_key(self, switches, client):
        """get_ports() should not fail if sortOrder is absent from query."""
        query = {"pageSize": 10, "page": 0}
        client.post.return_value = {}

        switches.get_ports(query_data=query)

        assert "sortOrder" not in query  # should remain absent

    def test_propagates_exception(self, switches, client):
        """get_ports() should propagate client exceptions."""
        client.post.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            switches.get_ports()


# =========================================================================
# configure_port()
# =========================================================================

class TestConfigurePort:
    """Tests for Switches.configure_port()."""

    def test_success(self, switches, client):
        """configure_port() should PUT kwargs to the port endpoint."""
        client.put.return_value = {"id": PORT_ID, "enabled": True}

        result = switches.configure_port(
            VENUE_ID, SWITCH_ID, PORT_ID, enabled=True, speed="1G"
        )

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/ports/{PORT_ID}",
            data={"enabled": True, "speed": "1G"},
        )
        assert result["enabled"] is True

    def test_not_found(self, switches, client):
        """configure_port() should raise ResourceNotFoundError on 404."""
        client.put.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=PORT_ID):
            switches.configure_port(VENUE_ID, SWITCH_ID, PORT_ID, enabled=False)


# =========================================================================
# get_vlans()
# =========================================================================

class TestGetVlans:
    """Tests for Switches.get_vlans()."""

    def test_success(self, switches, client):
        """get_vlans() should GET the vlans endpoint."""
        expected = [{"id": 100, "name": "Data"}, {"id": 200, "name": "Voice"}]
        client.get.return_value = expected

        result = switches.get_vlans(VENUE_ID, SWITCH_ID)

        client.get.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/vlans"
        )
        assert result == expected

    def test_not_found(self, switches, client):
        """get_vlans() should raise ResourceNotFoundError if switch missing."""
        client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.get_vlans(VENUE_ID, SWITCH_ID)

    def test_propagates_generic_exception(self, switches, client):
        """get_vlans() should re-raise non-404 exceptions."""
        client.get.side_effect = ValueError("unexpected")

        with pytest.raises(ValueError, match="unexpected"):
            switches.get_vlans(VENUE_ID, SWITCH_ID)


# =========================================================================
# configure_vlan()
# =========================================================================

class TestConfigureVlan:
    """Tests for Switches.configure_vlan()."""

    def test_success(self, switches, client):
        """configure_vlan() should PUT kwargs to the vlan endpoint."""
        client.put.return_value = {"id": VLAN_ID, "name": "Voice VLAN"}

        result = switches.configure_vlan(
            VENUE_ID, SWITCH_ID, VLAN_ID, name="Voice VLAN", igmpSnooping=True
        )

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/vlans/{VLAN_ID}",
            data={"name": "Voice VLAN", "igmpSnooping": True},
        )
        assert result["name"] == "Voice VLAN"

    def test_not_found(self, switches, client):
        """configure_vlan() should raise ResourceNotFoundError on 404."""
        client.put.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=str(VLAN_ID)):
            switches.configure_vlan(VENUE_ID, SWITCH_ID, VLAN_ID, name="X")

    def test_propagates_generic_exception(self, switches, client):
        """configure_vlan() should re-raise non-404 exceptions."""
        client.put.side_effect = ConnectionError("timeout")

        with pytest.raises(ConnectionError):
            switches.configure_vlan(VENUE_ID, SWITCH_ID, VLAN_ID, name="X")


# =========================================================================
# create_vlan()
# =========================================================================

class TestCreateVlan:
    """Tests for Switches.create_vlan()."""

    def test_success(self, switches, client):
        """create_vlan() should POST with vlan_id in the data body."""
        client.post.return_value = {"id": VLAN_ID, "name": "Data VLAN"}

        result = switches.create_vlan(
            VENUE_ID, SWITCH_ID, VLAN_ID, name="Data VLAN", igmpSnooping=False
        )

        client.post.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/vlans",
            data={"id": VLAN_ID, "name": "Data VLAN", "igmpSnooping": False},
        )
        assert result["id"] == VLAN_ID

    def test_id_in_data(self, switches, client):
        """create_vlan() must include 'id' equal to vlan_id in the payload."""
        client.post.return_value = {}

        switches.create_vlan(VENUE_ID, SWITCH_ID, 42)

        data = client.post.call_args[1]["data"]
        assert data["id"] == 42

    def test_kwargs_merged(self, switches, client):
        """Extra kwargs should be merged into the data payload."""
        client.post.return_value = {}

        switches.create_vlan(VENUE_ID, SWITCH_ID, 10, name="Mgmt", igmpSnooping=True)

        data = client.post.call_args[1]["data"]
        assert data == {"id": 10, "name": "Mgmt", "igmpSnooping": True}

    def test_not_found(self, switches, client):
        """create_vlan() should raise ResourceNotFoundError if switch missing."""
        client.post.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.create_vlan(VENUE_ID, SWITCH_ID, VLAN_ID)

    def test_propagates_generic_exception(self, switches, client):
        """create_vlan() should re-raise non-404 exceptions."""
        client.post.side_effect = RuntimeError("server error")

        with pytest.raises(RuntimeError, match="server error"):
            switches.create_vlan(VENUE_ID, SWITCH_ID, VLAN_ID)


# =========================================================================
# delete_vlan()
# =========================================================================

class TestDeleteVlan:
    """Tests for Switches.delete_vlan()."""

    def test_success(self, switches, client):
        """delete_vlan() should DELETE the correct endpoint."""
        client.delete.return_value = None

        result = switches.delete_vlan(VENUE_ID, SWITCH_ID, VLAN_ID)

        client.delete.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/vlans/{VLAN_ID}"
        )
        # delete_vlan returns None
        assert result is None

    def test_not_found(self, switches, client):
        """delete_vlan() should raise ResourceNotFoundError on 404."""
        client.delete.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=str(VLAN_ID)):
            switches.delete_vlan(VENUE_ID, SWITCH_ID, VLAN_ID)

    def test_propagates_generic_exception(self, switches, client):
        """delete_vlan() should re-raise non-404 exceptions."""
        client.delete.side_effect = PermissionError("forbidden")

        with pytest.raises(PermissionError):
            switches.delete_vlan(VENUE_ID, SWITCH_ID, VLAN_ID)


# =========================================================================
# get_statistics()
# =========================================================================

class TestGetStatistics:
    """Tests for Switches.get_statistics()."""

    def test_success(self, switches, client):
        """get_statistics() should GET the statistics endpoint."""
        expected = {"cpuUsage": 42, "memoryUsage": 65}
        client.get.return_value = expected

        result = switches.get_statistics(VENUE_ID, SWITCH_ID)

        client.get.assert_called_once_with(
            f"/venues/{VENUE_ID}/switches/{SWITCH_ID}/statistics"
        )
        assert result == expected

    def test_not_found(self, switches, client):
        """get_statistics() should raise ResourceNotFoundError on 404."""
        client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match=SWITCH_ID):
            switches.get_statistics(VENUE_ID, SWITCH_ID)


# =========================================================================
# add_to_venue() — default endpoint
# =========================================================================

class TestAddToVenue:
    """Tests for Switches.add_to_venue()."""

    def test_default_endpoint(self, switches, client):
        """add_to_venue() should POST to /venues/{id}/switches by default."""
        client.post.return_value = {"id": "SN123", "name": "Edge SW"}

        result = switches.add_to_venue(VENUE_ID, "SN123", "Edge SW")

        args, kwargs = client.post.call_args
        assert args[0] == f"/venues/{VENUE_ID}/switches"
        # API expects an array of switch objects
        payload = kwargs["data"]
        assert isinstance(payload, list)
        data = payload[0]
        assert data["id"] == "SN123"
        assert data["name"] == "Edge SW"
        assert data["venueId"] == VENUE_ID
        assert result["name"] == "Edge SW"

    def test_default_values(self, switches, client):
        """Default payload should include correct default field values."""
        client.post.return_value = {}

        switches.add_to_venue(VENUE_ID, "SN1", "SW1")

        data = client.post.call_args[1]["data"][0]
        assert data["enableStack"] is False
        assert data["jumboMode"] is False
        assert data["igmpSnooping"] == "none"
        assert data["rearModule"] == "none"
        assert data["specifiedType"] == "ROUTER"

    def test_optional_fields_omitted_when_none(self, switches, client):
        """Optional fields with None values should not appear in payload."""
        client.post.return_value = {}

        switches.add_to_venue(VENUE_ID, "SN1", "SW1")

        data = client.post.call_args[1]["data"][0]
        assert "description" not in data
        assert "trustPorts" not in data
        assert "stackMembers" not in data
        assert "spanningTreePriority" not in data
        assert "initialVlanId" not in data

    def test_optional_fields_included_when_set(self, switches, client):
        """Optional fields should appear when explicitly provided."""
        client.post.return_value = {}

        switches.add_to_venue(
            VENUE_ID,
            "SN1",
            "SW1",
            description="Main switch",
            trust_ports=["port1"],
            stack_members=[{"id": "m1"}],
            spanning_tree_priority=4096,
            initial_vlan_id=10,
        )

        data = client.post.call_args[1]["data"][0]
        assert data["description"] == "Main switch"
        assert data["trustPorts"] == ["port1"]
        assert data["stackMembers"] == [{"id": "m1"}]
        assert data["spanningTreePriority"] == 4096
        assert data["initialVlanId"] == 10

    def test_extra_kwargs_merged(self, switches, client):
        """Extra **kwargs should be merged into the payload."""
        client.post.return_value = {}

        switches.add_to_venue(VENUE_ID, "SN1", "SW1", customField="value")

        data = client.post.call_args[1]["data"][0]
        assert data["customField"] == "value"

    def test_simple_endpoint(self, switches, client):
        """use_simple_endpoint=True should POST to /switches."""
        client.post.return_value = {"id": "SN1"}

        switches.add_to_venue(
            VENUE_ID,
            "SN1",
            "SW1",
            use_simple_endpoint=True,
        )

        args, kwargs = client.post.call_args
        assert args[0] == "/switches"
        data = kwargs["data"][0]
        assert data["id"] == "SN1"
        assert data["name"] == "SW1"
        assert data["venueId"] == VENUE_ID
        assert data["stackMembers"] == []
        assert data["trustPorts"] == []

    def test_simple_endpoint_with_members(self, switches, client):
        """Simple endpoint should include stack_members and trust_ports when provided."""
        client.post.return_value = {}

        switches.add_to_venue(
            VENUE_ID,
            "SN1",
            "SW1",
            stack_members=[{"id": "m1"}],
            trust_ports=["p1", "p2"],
            use_simple_endpoint=True,
        )

        data = client.post.call_args[1]["data"][0]
        assert data["stackMembers"] == [{"id": "m1"}]
        assert data["trustPorts"] == ["p1", "p2"]

    def test_simple_endpoint_omits_advanced_fields(self, switches, client):
        """Simple endpoint payload should NOT include enableStack, jumboMode, etc."""
        client.post.return_value = {}

        switches.add_to_venue(VENUE_ID, "SN1", "SW1", use_simple_endpoint=True)

        data = client.post.call_args[1]["data"][0]
        assert "enableStack" not in data
        assert "jumboMode" not in data
        assert "igmpSnooping" not in data
        assert "rearModule" not in data
        assert "specifiedType" not in data

    def test_propagates_exception(self, switches, client):
        """add_to_venue() should propagate client exceptions."""
        client.post.side_effect = RuntimeError("API failure")

        with pytest.raises(RuntimeError, match="API failure"):
            switches.add_to_venue(VENUE_ID, "SN1", "SW1")


# =========================================================================
# Module construction
# =========================================================================

class TestConstruction:
    """Tests for Switches module construction."""

    def test_stores_client_reference(self, switches, client):
        """The client attribute should be the injected mock."""
        assert switches.client is client

    def test_instantiation_with_mock(self):
        """Switches should accept any object as client."""
        mock = MagicMock()
        s = Switches(mock)
        assert s.client is mock


# ── list_all ─────────────────────────────────────────────────────────────


class TestListAll:
    """Tests for Switches.list_all()."""

    def test_delegates_to_paginate_query(self, switches):
        switches.client.paginate_query.return_value = [{"id": "sw1"}]
        result = switches.list_all()
        switches.client.paginate_query.assert_called_once_with("/venues/switches/query", None)
        assert result == [{"id": "sw1"}]

    def test_passes_query_data(self, switches):
        switches.client.paginate_query.return_value = []
        q = {"filters": [{"type": "VENUE", "value": "v1"}]}
        switches.list_all(query_data=q)
        switches.client.paginate_query.assert_called_once_with("/venues/switches/query", q)
