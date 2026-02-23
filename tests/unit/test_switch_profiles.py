"""Comprehensive unit tests for the SwitchProfiles module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.switch_profiles import SwitchProfiles


@pytest.fixture
def switch_profiles(mock_client):
    """Create a SwitchProfiles instance backed by a mock client."""
    return SwitchProfiles(mock_client)


# ── list ────────────────────────────────────────────────────────────────────


class TestList:
    """Tests for SwitchProfiles.list()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        switch_profiles.client.get.return_value = []
        switch_profiles.list()
        switch_profiles.client.get.assert_called_once_with("/switchProfiles")

    def test_returns_list_when_response_is_list(self, switch_profiles):
        expected = [{"id": "p1", "name": "Profile 1"}, {"id": "p2", "name": "Profile 2"}]
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.list() == expected

    def test_returns_empty_list_when_response_is_not_list(self, switch_profiles):
        switch_profiles.client.get.return_value = {"unexpected": "dict"}
        assert switch_profiles.list() == []

    def test_returns_empty_list_when_response_is_none(self, switch_profiles):
        switch_profiles.client.get.return_value = None
        assert switch_profiles.list() == []

    def test_returns_empty_list_when_response_is_string(self, switch_profiles):
        switch_profiles.client.get.return_value = "not a list"
        assert switch_profiles.list() == []

    def test_propagates_exception(self, switch_profiles):
        switch_profiles.client.get.side_effect = RuntimeError("connection lost")
        with pytest.raises(RuntimeError, match="connection lost"):
            switch_profiles.list()


# ── get ─────────────────────────────────────────────────────────────────────


class TestGet:
    """Tests for SwitchProfiles.get()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        profile_id = "sp-abc-123"
        switch_profiles.get(profile_id)
        switch_profiles.client.get.assert_called_once_with(f"/switchProfiles/{profile_id}")

    def test_returns_profile_dict(self, switch_profiles):
        expected = {"id": "sp-abc-123", "name": "Default Profile"}
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.get("sp-abc-123") == expected

    def test_404_raises_resource_not_found_with_message(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.get("bad-id")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.get("bad-id")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.get.side_effect = ValueError("unexpected")
        with pytest.raises(ValueError, match="unexpected"):
            switch_profiles.get("x")


# ── create ──────────────────────────────────────────────────────────────────


class TestCreate:
    """Tests for SwitchProfiles.create()."""

    def test_posts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.create(name="Test Profile")
        args, kwargs = switch_profiles.client.post.call_args
        assert args[0] == "/switchProfiles"

    def test_required_fields_in_payload(self, switch_profiles):
        switch_profiles.create(name="Test Profile")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["name"] == "Test Profile"
        assert data["profileType"] == "Regular"
        assert data["applyOnboardOnly"] is False

    def test_description_included_when_provided(self, switch_profiles):
        switch_profiles.create(name="Test", description="A test profile")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["description"] == "A test profile"

    def test_description_omitted_when_none(self, switch_profiles):
        switch_profiles.create(name="Test")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert "description" not in data

    def test_description_omitted_when_empty_string(self, switch_profiles):
        """Empty string is falsy, so description should be omitted."""
        switch_profiles.create(name="Test", description="")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert "description" not in data

    def test_custom_profile_type(self, switch_profiles):
        switch_profiles.create(name="Template", profile_type="Template")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["profileType"] == "Template"

    def test_apply_onboard_only_true(self, switch_profiles):
        switch_profiles.create(name="Onboard", apply_onboard_only=True)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["applyOnboardOnly"] is True

    def test_kwargs_merged_into_payload(self, switch_profiles):
        switch_profiles.create(name="Test", venueId="v-1", firmware="10.5")
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["venueId"] == "v-1"
        assert data["firmware"] == "10.5"

    def test_returns_created_profile(self, switch_profiles):
        expected = {"id": "sp-new", "name": "Test Profile"}
        switch_profiles.client.post.return_value = expected
        result = switch_profiles.create(name="Test Profile")
        assert result == expected

    def test_propagates_exception(self, switch_profiles):
        switch_profiles.client.post.side_effect = RuntimeError("server error")
        with pytest.raises(RuntimeError, match="server error"):
            switch_profiles.create(name="Test")


# ── update ──────────────────────────────────────────────────────────────────


class TestUpdate:
    """Tests for SwitchProfiles.update()."""

    def test_puts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.update("sp-123", name="Updated")
        args, _ = switch_profiles.client.put.call_args
        assert args[0] == "/switchProfiles/sp-123"

    def test_kwargs_sent_as_data(self, switch_profiles):
        switch_profiles.update("sp-123", name="Renamed", description="New desc")
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {"name": "Renamed", "description": "New desc"}

    def test_empty_kwargs_sends_empty_dict(self, switch_profiles):
        switch_profiles.update("sp-123")
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {}

    def test_returns_updated_profile(self, switch_profiles):
        expected = {"id": "sp-123", "name": "Renamed"}
        switch_profiles.client.put.return_value = expected
        assert switch_profiles.update("sp-123", name="Renamed") == expected

    def test_404_raises_resource_not_found_with_message(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID gone-id not found"):
            switch_profiles.update("gone-id", name="x")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.update("gone-id", name="x")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.put.side_effect = ConnectionError("timeout")
        with pytest.raises(ConnectionError, match="timeout"):
            switch_profiles.update("sp-123", name="x")


# ── delete ──────────────────────────────────────────────────────────────────


class TestDelete:
    """Tests for SwitchProfiles.delete()."""

    def test_deletes_correct_endpoint(self, switch_profiles):
        switch_profiles.delete("sp-123")
        switch_profiles.client.delete.assert_called_once_with("/switchProfiles/sp-123")

    def test_returns_none(self, switch_profiles):
        switch_profiles.client.delete.return_value = None
        result = switch_profiles.delete("sp-123")
        assert result is None

    def test_404_raises_resource_not_found_with_message(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID gone-id not found"):
            switch_profiles.delete("gone-id")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.delete("gone-id")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.delete.side_effect = PermissionError("forbidden")
        with pytest.raises(PermissionError, match="forbidden"):
            switch_profiles.delete("sp-123")


# ── query ───────────────────────────────────────────────────────────────────


class TestQuery:
    """Tests for SwitchProfiles.query()."""

    def test_posts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.query()
        args, _ = switch_profiles.client.post.call_args
        assert args[0] == "/switchProfiles/query"

    def test_default_query_data(self, switch_profiles):
        switch_profiles.query()
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data == {"pageSize": 100, "page": 1, "sortOrder": "ASC"}

    def test_custom_query_data(self, switch_profiles):
        custom = {"pageSize": 50, "page": 2, "sortOrder": "DESC"}
        switch_profiles.query(query_data=custom)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["pageSize"] == 50
        assert data["page"] == 2
        assert data["sortOrder"] == "DESC"

    def test_sort_order_uppercased(self, switch_profiles):
        switch_profiles.query(query_data={"sortOrder": "desc"})
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["sortOrder"] == "DESC"

    def test_query_with_filters(self, switch_profiles):
        query = {
            "filters": [{"type": "NAME", "value": "test"}],
            "pageSize": 25,
            "page": 1,
            "sortOrder": "ASC"
        }
        switch_profiles.query(query_data=query)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data["filters"] == [{"type": "NAME", "value": "test"}]

    def test_returns_query_response(self, switch_profiles):
        expected = {"data": [{"id": "sp-1"}], "totalCount": 1}
        switch_profiles.client.post.return_value = expected
        assert switch_profiles.query() == expected

    def test_propagates_exception(self, switch_profiles):
        switch_profiles.client.post.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            switch_profiles.query()


# ── get_acls ────────────────────────────────────────────────────────────────


class TestGetAcls:
    """Tests for SwitchProfiles.get_acls()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        switch_profiles.client.get.return_value = []
        switch_profiles.get_acls("sp-123")
        switch_profiles.client.get.assert_called_once_with("/switchProfiles/sp-123/acls")

    def test_returns_list_when_response_is_list(self, switch_profiles):
        expected = [{"id": "acl-1", "name": "Block SSH"}]
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.get_acls("sp-123") == expected

    def test_returns_empty_list_when_response_is_not_list(self, switch_profiles):
        switch_profiles.client.get.return_value = {"unexpected": "value"}
        assert switch_profiles.get_acls("sp-123") == []

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.get_acls("bad-id")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.get_acls("bad-id")
        assert exc_info.value.status_code == 404


# ── add_acl ─────────────────────────────────────────────────────────────────


class TestAddAcl:
    """Tests for SwitchProfiles.add_acl()."""

    def test_posts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.add_acl("sp-123", {"name": "Allow HTTP"})
        args, _ = switch_profiles.client.post.call_args
        assert args[0] == "/switchProfiles/sp-123/acls"

    def test_acl_data_sent_as_data(self, switch_profiles):
        acl_data = {"name": "Allow HTTP", "action": "permit", "protocol": "tcp"}
        switch_profiles.add_acl("sp-123", acl_data)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data == acl_data

    def test_returns_created_acl(self, switch_profiles):
        expected = {"id": "acl-new", "name": "Allow HTTP"}
        switch_profiles.client.post.return_value = expected
        assert switch_profiles.add_acl("sp-123", {"name": "Allow HTTP"}) == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.add_acl("bad-id", {"name": "test"})

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.post.side_effect = ValueError("bad data")
        with pytest.raises(ValueError, match="bad data"):
            switch_profiles.add_acl("sp-123", {"name": "test"})


# ── update_acl ──────────────────────────────────────────────────────────────


class TestUpdateAcl:
    """Tests for SwitchProfiles.update_acl()."""

    def test_puts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.update_acl("sp-123", "acl-456", name="Updated ACL")
        args, _ = switch_profiles.client.put.call_args
        assert args[0] == "/switchProfiles/sp-123/acls/acl-456"

    def test_kwargs_sent_as_data(self, switch_profiles):
        switch_profiles.update_acl("sp-123", "acl-456", name="Renamed", action="deny")
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {"name": "Renamed", "action": "deny"}

    def test_returns_updated_acl(self, switch_profiles):
        expected = {"id": "acl-456", "name": "Updated ACL"}
        switch_profiles.client.put.return_value = expected
        assert switch_profiles.update_acl("sp-123", "acl-456", name="Updated ACL") == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile sp-123 or ACL acl-bad not found"):
            switch_profiles.update_acl("sp-123", "acl-bad", name="x")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.update_acl("sp-123", "acl-bad", name="x")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.put.side_effect = ConnectionError("timeout")
        with pytest.raises(ConnectionError, match="timeout"):
            switch_profiles.update_acl("sp-123", "acl-456", name="x")


# ── delete_acl ──────────────────────────────────────────────────────────────


class TestDeleteAcl:
    """Tests for SwitchProfiles.delete_acl()."""

    def test_deletes_correct_endpoint(self, switch_profiles):
        switch_profiles.delete_acl("sp-123", "acl-456")
        switch_profiles.client.delete.assert_called_once_with("/switchProfiles/sp-123/acls/acl-456")

    def test_returns_none(self, switch_profiles):
        switch_profiles.client.delete.return_value = None
        result = switch_profiles.delete_acl("sp-123", "acl-456")
        assert result is None

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile sp-123 or ACL acl-bad not found"):
            switch_profiles.delete_acl("sp-123", "acl-bad")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.delete_acl("sp-123", "acl-bad")
        assert exc_info.value.status_code == 404


# ── get_vlans ───────────────────────────────────────────────────────────────


class TestGetVlans:
    """Tests for SwitchProfiles.get_vlans()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        switch_profiles.client.get.return_value = []
        switch_profiles.get_vlans("sp-123")
        switch_profiles.client.get.assert_called_once_with("/switchProfiles/sp-123/vlans")

    def test_returns_list_when_response_is_list(self, switch_profiles):
        expected = [{"id": "vlan-1", "vlanId": 100}]
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.get_vlans("sp-123") == expected

    def test_returns_empty_list_when_response_is_not_list(self, switch_profiles):
        switch_profiles.client.get.return_value = None
        assert switch_profiles.get_vlans("sp-123") == []

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.get_vlans("bad-id")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.get_vlans("bad-id")
        assert exc_info.value.status_code == 404


# ── add_vlan ────────────────────────────────────────────────────────────────


class TestAddVlan:
    """Tests for SwitchProfiles.add_vlan()."""

    def test_posts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.add_vlan("sp-123", {"vlanId": 200})
        args, _ = switch_profiles.client.post.call_args
        assert args[0] == "/switchProfiles/sp-123/vlans"

    def test_vlan_data_sent_as_data(self, switch_profiles):
        vlan_data = {"vlanId": 200, "name": "Guest"}
        switch_profiles.add_vlan("sp-123", vlan_data)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data == vlan_data

    def test_returns_created_vlan(self, switch_profiles):
        expected = {"id": "vlan-new", "vlanId": 200}
        switch_profiles.client.post.return_value = expected
        assert switch_profiles.add_vlan("sp-123", {"vlanId": 200}) == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.add_vlan("bad-id", {"vlanId": 100})

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.post.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="fail"):
            switch_profiles.add_vlan("sp-123", {"vlanId": 100})


# ── update_vlan ─────────────────────────────────────────────────────────────


class TestUpdateVlan:
    """Tests for SwitchProfiles.update_vlan()."""

    def test_puts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.update_vlan("sp-123", "vlan-456", name="Updated")
        args, _ = switch_profiles.client.put.call_args
        assert args[0] == "/switchProfiles/sp-123/vlans/vlan-456"

    def test_kwargs_sent_as_data(self, switch_profiles):
        switch_profiles.update_vlan("sp-123", "vlan-456", name="Corp", vlanId=300)
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {"name": "Corp", "vlanId": 300}

    def test_returns_updated_vlan(self, switch_profiles):
        expected = {"id": "vlan-456", "name": "Updated"}
        switch_profiles.client.put.return_value = expected
        assert switch_profiles.update_vlan("sp-123", "vlan-456", name="Updated") == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile sp-123 or VLAN vlan-bad not found"):
            switch_profiles.update_vlan("sp-123", "vlan-bad", name="x")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.update_vlan("sp-123", "vlan-bad", name="x")
        assert exc_info.value.status_code == 404


# ── delete_vlan ─────────────────────────────────────────────────────────────


class TestDeleteVlan:
    """Tests for SwitchProfiles.delete_vlan()."""

    def test_deletes_correct_endpoint(self, switch_profiles):
        switch_profiles.delete_vlan("sp-123", "vlan-456")
        switch_profiles.client.delete.assert_called_once_with("/switchProfiles/sp-123/vlans/vlan-456")

    def test_returns_none(self, switch_profiles):
        switch_profiles.client.delete.return_value = None
        result = switch_profiles.delete_vlan("sp-123", "vlan-456")
        assert result is None

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile sp-123 or VLAN vlan-bad not found"):
            switch_profiles.delete_vlan("sp-123", "vlan-bad")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.delete_vlan("sp-123", "vlan-bad")
        assert exc_info.value.status_code == 404


# ── get_trusted_ports ───────────────────────────────────────────────────────


class TestGetTrustedPorts:
    """Tests for SwitchProfiles.get_trusted_ports()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        switch_profiles.client.get.return_value = []
        switch_profiles.get_trusted_ports("sp-123")
        switch_profiles.client.get.assert_called_once_with("/switchProfiles/sp-123/trustedPorts")

    def test_returns_list_when_response_is_list(self, switch_profiles):
        expected = [{"id": "port-1", "portName": "ge-0/0/1"}]
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.get_trusted_ports("sp-123") == expected

    def test_returns_empty_list_when_response_is_not_list(self, switch_profiles):
        switch_profiles.client.get.return_value = {"unexpected": True}
        assert switch_profiles.get_trusted_ports("sp-123") == []

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.get_trusted_ports("bad-id")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.get_trusted_ports("bad-id")
        assert exc_info.value.status_code == 404


# ── add_trusted_port ────────────────────────────────────────────────────────


class TestAddTrustedPort:
    """Tests for SwitchProfiles.add_trusted_port()."""

    def test_posts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.add_trusted_port("sp-123", {"portName": "ge-0/0/1"})
        args, _ = switch_profiles.client.post.call_args
        assert args[0] == "/switchProfiles/sp-123/trustedPorts"

    def test_port_data_sent_as_data(self, switch_profiles):
        port_data = {"portName": "ge-0/0/1", "trusted": True}
        switch_profiles.add_trusted_port("sp-123", port_data)
        data = switch_profiles.client.post.call_args[1]["data"]
        assert data == port_data

    def test_returns_created_port(self, switch_profiles):
        expected = {"id": "port-new", "portName": "ge-0/0/1"}
        switch_profiles.client.post.return_value = expected
        assert switch_profiles.add_trusted_port("sp-123", {"portName": "ge-0/0/1"}) == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile with ID bad-id not found"):
            switch_profiles.add_trusted_port("bad-id", {"portName": "ge-0/0/1"})

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.post.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="fail"):
            switch_profiles.add_trusted_port("sp-123", {"portName": "ge-0/0/1"})


# ── update_trusted_port ────────────────────────────────────────────────────


class TestUpdateTrustedPort:
    """Tests for SwitchProfiles.update_trusted_port()."""

    def test_puts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.update_trusted_port("sp-123", "port-456", trusted=False)
        args, _ = switch_profiles.client.put.call_args
        assert args[0] == "/switchProfiles/sp-123/trustedPorts/port-456"

    def test_kwargs_sent_as_data(self, switch_profiles):
        switch_profiles.update_trusted_port("sp-123", "port-456", portName="ge-0/0/2", trusted=True)
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {"portName": "ge-0/0/2", "trusted": True}

    def test_returns_updated_port(self, switch_profiles):
        expected = {"id": "port-456", "trusted": False}
        switch_profiles.client.put.return_value = expected
        assert switch_profiles.update_trusted_port("sp-123", "port-456", trusted=False) == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Switch profile sp-123 or trusted port port-bad not found"):
            switch_profiles.update_trusted_port("sp-123", "port-bad", trusted=True)

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.update_trusted_port("sp-123", "port-bad", trusted=True)
        assert exc_info.value.status_code == 404


# ── delete_trusted_port ────────────────────────────────────────────────────


class TestDeleteTrustedPort:
    """Tests for SwitchProfiles.delete_trusted_port()."""

    def test_deletes_correct_endpoint(self, switch_profiles):
        switch_profiles.delete_trusted_port("sp-123", "port-456")
        switch_profiles.client.delete.assert_called_once_with(
            "/switchProfiles/sp-123/trustedPorts/port-456"
        )

    def test_returns_none(self, switch_profiles):
        switch_profiles.client.delete.return_value = None
        result = switch_profiles.delete_trusted_port("sp-123", "port-456")
        assert result is None

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(
            ResourceNotFoundError,
            match="Switch profile sp-123 or trusted port port-bad not found"
        ):
            switch_profiles.delete_trusted_port("sp-123", "port-bad")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.delete_trusted_port("sp-123", "port-bad")
        assert exc_info.value.status_code == 404


# ── associate_with_venue ────────────────────────────────────────────────────


class TestAssociateWithVenue:
    """Tests for SwitchProfiles.associate_with_venue()."""

    def test_puts_to_correct_endpoint(self, switch_profiles):
        switch_profiles.associate_with_venue("v-100", "sp-123")
        args, _ = switch_profiles.client.put.call_args
        assert args[0] == "/venues/v-100/switchProfiles/sp-123"

    def test_kwargs_sent_as_data(self, switch_profiles):
        switch_profiles.associate_with_venue("v-100", "sp-123", priority=1)
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {"priority": 1}

    def test_empty_kwargs_sends_empty_dict(self, switch_profiles):
        switch_profiles.associate_with_venue("v-100", "sp-123")
        data = switch_profiles.client.put.call_args[1]["data"]
        assert data == {}

    def test_returns_association_result(self, switch_profiles):
        expected = {"status": "associated"}
        switch_profiles.client.put.return_value = expected
        assert switch_profiles.associate_with_venue("v-100", "sp-123") == expected

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(
            ResourceNotFoundError,
            match="Venue v-100 or switch profile sp-bad not found"
        ):
            switch_profiles.associate_with_venue("v-100", "sp-bad")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.associate_with_venue("v-100", "sp-bad")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.put.side_effect = RuntimeError("server error")
        with pytest.raises(RuntimeError, match="server error"):
            switch_profiles.associate_with_venue("v-100", "sp-123")


# ── disassociate_from_venue ─────────────────────────────────────────────────


class TestDisassociateFromVenue:
    """Tests for SwitchProfiles.disassociate_from_venue()."""

    def test_deletes_correct_endpoint(self, switch_profiles):
        switch_profiles.disassociate_from_venue("v-100", "sp-123")
        switch_profiles.client.delete.assert_called_once_with(
            "/venues/v-100/switchProfiles/sp-123"
        )

    def test_returns_none(self, switch_profiles):
        switch_profiles.client.delete.return_value = None
        result = switch_profiles.disassociate_from_venue("v-100", "sp-123")
        assert result is None

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(
            ResourceNotFoundError,
            match="Venue v-100 or switch profile sp-bad not found"
        ):
            switch_profiles.disassociate_from_venue("v-100", "sp-bad")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.disassociate_from_venue("v-100", "sp-bad")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.delete.side_effect = IOError("network down")
        with pytest.raises(IOError, match="network down"):
            switch_profiles.disassociate_from_venue("v-100", "sp-123")


# ── get_venue_profiles ──────────────────────────────────────────────────────


class TestGetVenueProfiles:
    """Tests for SwitchProfiles.get_venue_profiles()."""

    def test_gets_correct_endpoint(self, switch_profiles):
        switch_profiles.client.get.return_value = []
        switch_profiles.get_venue_profiles("v-100")
        switch_profiles.client.get.assert_called_once_with("/venues/v-100/switchProfiles")

    def test_returns_list_when_response_is_list(self, switch_profiles):
        expected = [{"id": "sp-1", "name": "Profile A"}, {"id": "sp-2", "name": "Profile B"}]
        switch_profiles.client.get.return_value = expected
        assert switch_profiles.get_venue_profiles("v-100") == expected

    def test_returns_empty_list_when_response_is_not_list(self, switch_profiles):
        switch_profiles.client.get.return_value = {"not": "a list"}
        assert switch_profiles.get_venue_profiles("v-100") == []

    def test_returns_empty_list_when_response_is_none(self, switch_profiles):
        switch_profiles.client.get.return_value = None
        assert switch_profiles.get_venue_profiles("v-100") == []

    def test_404_raises_resource_not_found(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Venue with ID bad-v not found"):
            switch_profiles.get_venue_profiles("bad-v")

    def test_404_preserves_status_code(self, switch_profiles):
        switch_profiles.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            switch_profiles.get_venue_profiles("bad-v")
        assert exc_info.value.status_code == 404

    def test_non_404_exception_propagates(self, switch_profiles):
        switch_profiles.client.get.side_effect = TimeoutError("slow")
        with pytest.raises(TimeoutError, match="slow"):
            switch_profiles.get_venue_profiles("v-100")


# ── bulk_delete ─────────────────────────────────────────────────────────────


class TestBulkDelete:
    """Tests for SwitchProfiles.bulk_delete()."""

    def test_calls_request_with_delete_method(self, switch_profiles):
        ids = ["sp-1", "sp-2", "sp-3"]
        switch_profiles.bulk_delete(ids)
        switch_profiles.client.request.assert_called_once_with(
            "DELETE", "/switchProfiles", json_data=ids
        )

    def test_sends_profile_ids_as_json_data(self, switch_profiles):
        ids = ["sp-a", "sp-b"]
        switch_profiles.bulk_delete(ids)
        _, kwargs = switch_profiles.client.request.call_args
        assert kwargs["json_data"] == ids

    def test_returns_bulk_delete_result(self, switch_profiles):
        expected = {"deleted": 3, "failed": 0}
        switch_profiles.client.request.return_value = expected
        assert switch_profiles.bulk_delete(["sp-1", "sp-2", "sp-3"]) == expected

    def test_empty_list(self, switch_profiles):
        switch_profiles.bulk_delete([])
        switch_profiles.client.request.assert_called_once_with(
            "DELETE", "/switchProfiles", json_data=[]
        )

    def test_single_id(self, switch_profiles):
        switch_profiles.bulk_delete(["sp-only"])
        switch_profiles.client.request.assert_called_once_with(
            "DELETE", "/switchProfiles", json_data=["sp-only"]
        )

    def test_propagates_exception(self, switch_profiles):
        switch_profiles.client.request.side_effect = RuntimeError("bulk fail")
        with pytest.raises(RuntimeError, match="bulk fail"):
            switch_profiles.bulk_delete(["sp-1"])


# ── constructor ─────────────────────────────────────────────────────────────


class TestConstructor:
    """Tests for SwitchProfiles.__init__."""

    def test_stores_client_reference(self):
        client = MagicMock()
        sp = SwitchProfiles(client)
        assert sp.client is client


# ── CLI variable / switch mapping helpers ───────────────────────────────────


def _cli_profile(variables=None, venue_switches=None):
    """Helper to build a CLI profile response."""
    return {
        'id': 'p1',
        'name': 'Test CLI Profile',
        'profileType': 'CLI',
        'venueCliTemplate': {
            'variables': variables or [],
            'venueSwitches': venue_switches or [],
        },
        'venues': [],
    }


def _non_cli_profile():
    """Helper to build a non-CLI profile response."""
    return {
        'id': 'p1',
        'name': 'Regular Profile',
        'profileType': 'Regular',
    }


@pytest.fixture
def sp():
    """Minimal SwitchProfiles backed by a MagicMock client."""
    client = MagicMock()
    return SwitchProfiles(client)


# ── get_cli_variables ───────────────────────────────────────────────────────


class TestGetCliVariables:
    """Tests for SwitchProfiles.get_cli_variables()."""

    def test_returns_variables_from_cli_profile(self, sp):
        variables = [{'name': 'vlan_id', 'type': 'NUMBER', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        result = sp.get_cli_variables('p1')
        assert result == variables
        sp.client.get.assert_called_once_with('/switchProfiles/p1')

    def test_returns_empty_list_when_no_variables(self, sp):
        sp.client.get.return_value = _cli_profile()
        assert sp.get_cli_variables('p1') == []

    def test_returns_empty_list_when_no_venue_cli_template(self, sp):
        profile = _cli_profile()
        del profile['venueCliTemplate']
        sp.client.get.return_value = profile
        assert sp.get_cli_variables('p1') == []

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_cli_variables('p1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_cli_variables('p1')


# ── update_cli_variables ────────────────────────────────────────────────────


class TestUpdateCliVariables:
    """Tests for SwitchProfiles.update_cli_variables()."""

    def test_puts_correct_payload(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {'id': 'p1', 'updated': True}
        new_vars = [{'name': 'hostname', 'type': 'TEXT', 'value': 'sw1'}]

        result = sp.update_cli_variables('p1', new_vars)

        expected_payload = {
            'id': 'p1',
            'name': 'Test CLI Profile',
            'profileType': 'CLI',
            'venueCliTemplate': {
                'variables': new_vars,
                'venueSwitches': [],
            },
            'venues': [],
        }
        sp.client.put.assert_called_once_with('/switchProfiles/p1', data=expected_payload)
        assert result == {'id': 'p1', 'updated': True}

    def test_preserves_existing_venue_switches(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.update_cli_variables('p1', [{'name': 'x'}])

        put_data = sp.client.put.call_args[1]['data']
        assert put_data['venueCliTemplate']['venueSwitches'] == vs

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.update_cli_variables('p1', [])

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_cli_variables('p1', [])


# ── add_cli_variable ───────────────────────────────────────────────────────


class TestAddCliVariable:
    """Tests for SwitchProfiles.add_cli_variable()."""

    def test_appends_variable_and_calls_update(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'existing', 'value': '1'}]
        )
        sp.client.put.return_value = {'id': 'p1'}

        new_var = {'name': 'new_var', 'type': 'TEXT', 'value': 'hello'}
        sp.add_cli_variable('p1', new_var)

        put_data = sp.client.put.call_args[1]['data']
        var_names = [v['name'] for v in put_data['venueCliTemplate']['variables']]
        assert 'existing' in var_names
        assert 'new_var' in var_names

    def test_raises_value_error_for_duplicate_name(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'dup', 'value': '1'}]
        )
        with pytest.raises(ValueError, match="already exists"):
            sp.add_cli_variable('p1', {'name': 'dup', 'value': '2'})

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.add_cli_variable('p1', {'name': 'x'})

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.add_cli_variable('p1', {'name': 'x'})

    def test_adds_to_empty_variables_list(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {}

        sp.add_cli_variable('p1', {'name': 'first', 'value': '1'})

        put_data = sp.client.put.call_args[1]['data']
        assert len(put_data['venueCliTemplate']['variables']) == 1
        assert put_data['venueCliTemplate']['variables'][0]['name'] == 'first'


# ── update_cli_variable ────────────────────────────────────────────────────


class TestUpdateCliVariable:
    """Tests for SwitchProfiles.update_cli_variable()."""

    def test_replaces_matching_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[
                {'name': 'keep', 'value': 'a'},
                {'name': 'target', 'value': 'old'},
            ]
        )
        sp.client.put.return_value = {}

        sp.update_cli_variable('p1', 'target', {'name': 'target', 'value': 'new'})

        put_data = sp.client.put.call_args[1]['data']
        variables = put_data['venueCliTemplate']['variables']
        target = next(v for v in variables if v['name'] == 'target')
        assert target['value'] == 'new'
        # The other variable should be unchanged
        keep = next(v for v in variables if v['name'] == 'keep')
        assert keep['value'] == 'a'

    def test_raises_resource_not_found_for_missing_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'other', 'value': '1'}]
        )
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_cli_variable('p1', 'nonexistent', {'name': 'nonexistent', 'value': '1'})

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.update_cli_variable('p1', 'x', {'name': 'x'})

    def test_propagates_resource_not_found_on_profile(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_cli_variable('p1', 'x', {'name': 'x'})


# ── delete_cli_variable ────────────────────────────────────────────────────


class TestDeleteCliVariable:
    """Tests for SwitchProfiles.delete_cli_variable()."""

    def test_removes_variable_by_name(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[
                {'name': 'keep', 'value': 'a'},
                {'name': 'remove', 'value': 'b'},
            ]
        )
        sp.client.put.return_value = {}

        sp.delete_cli_variable('p1', 'remove')

        put_data = sp.client.put.call_args[1]['data']
        variables = put_data['venueCliTemplate']['variables']
        assert len(variables) == 1
        assert variables[0]['name'] == 'keep'

    def test_raises_resource_not_found_for_missing_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'other', 'value': '1'}]
        )
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.delete_cli_variable('p1', 'nonexistent')

    def test_raises_resource_not_found_on_empty_variables(self, sp):
        sp.client.get.return_value = _cli_profile()
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.delete_cli_variable('p1', 'anything')

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.delete_cli_variable('p1', 'x')

    def test_propagates_resource_not_found_on_profile(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.delete_cli_variable('p1', 'x')


# ── get_cli_profile_switches ───────────────────────────────────────────────


class TestGetCliProfileSwitches:
    """Tests for SwitchProfiles.get_cli_profile_switches()."""

    def test_returns_switches_for_venue(self, sp):
        vs = [
            {'venueId': 'v1', 'switches': ['sw1', 'sw2']},
            {'venueId': 'v2', 'switches': ['sw3']},
        ]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        assert sp.get_cli_profile_switches('p1', 'v1') == ['sw1', 'sw2']

    def test_returns_switches_for_second_venue(self, sp):
        vs = [
            {'venueId': 'v1', 'switches': ['sw1']},
            {'venueId': 'v2', 'switches': ['sw3']},
        ]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        assert sp.get_cli_profile_switches('p1', 'v2') == ['sw3']

    def test_returns_empty_list_for_unknown_venue(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        assert sp.get_cli_profile_switches('p1', 'v999') == []

    def test_returns_empty_list_when_no_venue_switches(self, sp):
        sp.client.get.return_value = _cli_profile()
        assert sp.get_cli_profile_switches('p1', 'v1') == []

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_cli_profile_switches('p1', 'v1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_cli_profile_switches('p1', 'v1')


# ── map_switch_to_cli_profile ──────────────────────────────────────────────


class TestMapSwitchToCliProfile:
    """Tests for SwitchProfiles.map_switch_to_cli_profile()."""

    def test_adds_switch_to_existing_venue(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {'id': 'p1'}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw2')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert len(venue_sw) == 1
        assert 'sw2' in venue_sw[0]['switches']
        assert 'sw1' in venue_sw[0]['switches']

    def test_creates_new_venue_mapping(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {'id': 'p1'}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert len(venue_sw) == 1
        assert venue_sw[0]['venueId'] == 'v1'
        assert venue_sw[0]['switches'] == ['sw1']

    def test_does_not_duplicate_existing_switch(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert venue_sw[0]['switches'] == ['sw1']

    def test_stores_variable_values(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw1', variable_values={'vlan_id': '100'})

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert venue_sw[0]['switchVariables']['sw1'] == {'vlan_id': '100'}

    def test_no_switch_variables_key_without_variable_values(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert 'switchVariables' not in venue_sw[0]

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

    def test_calls_update_with_name_kwarg(self, sp):
        sp.client.get.return_value = _cli_profile()
        sp.client.put.return_value = {}

        sp.map_switch_to_cli_profile('p1', 'v1', 'sw1')

        sp.client.put.assert_called_once()
        put_kwargs = sp.client.put.call_args[1]['data']
        assert put_kwargs['name'] == 'Test CLI Profile'


# ── unmap_switch_from_cli_profile ───────────────────────────────────────────


class TestUnmapSwitchFromCliProfile:
    """Tests for SwitchProfiles.unmap_switch_from_cli_profile()."""

    def test_removes_switch_from_venue(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1', 'sw2']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert len(venue_sw) == 1
        assert venue_sw[0]['switches'] == ['sw2']

    def test_removes_empty_venue_mapping(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert venue_sw == []

    def test_removes_switch_variables_for_switch(self, sp):
        vs = [{
            'venueId': 'v1',
            'switches': ['sw1', 'sw2'],
            'switchVariables': {'sw1': {'vlan': '10'}, 'sw2': {'vlan': '20'}},
        }]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw1')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert 'sw1' not in venue_sw[0].get('switchVariables', {})
        assert venue_sw[0]['switchVariables']['sw2'] == {'vlan': '20'}

    def test_no_error_when_switch_not_in_venue(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        # Should not raise -- just leaves venue intact
        sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw999')

        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert venue_sw[0]['switches'] == ['sw1']

    def test_no_error_when_venue_not_found(self, sp):
        vs = [{'venueId': 'v1', 'switches': ['sw1']}]
        sp.client.get.return_value = _cli_profile(venue_switches=vs)
        sp.client.put.return_value = {}

        sp.unmap_switch_from_cli_profile('p1', 'v999', 'sw1')

        # Venue v1 should remain untouched
        put_kwargs = sp.client.put.call_args[1]['data']
        venue_sw = put_kwargs['venueCliTemplate']['venueSwitches']
        assert len(venue_sw) == 1
        assert venue_sw[0]['switches'] == ['sw1']

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.unmap_switch_from_cli_profile('p1', 'v1', 'sw1')


# ── get_switch_variable_values ──────────────────────────────────────────────


class TestGetSwitchVariableValues:
    """Tests for SwitchProfiles.get_switch_variable_values()."""

    def test_returns_switch_specific_values(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                    {'serialNumbers': ['SN2'], 'value': '300'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        result = sp.get_switch_variable_values('p1', 'SN1')
        assert result == {'vlan_id': '200'}

    def test_falls_back_to_default_value(self, sp):
        variables = [
            {
                'name': 'hostname',
                'value': 'default-host',
                'switchVariables': [
                    {'serialNumbers': ['SN_OTHER'], 'value': 'other-host'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        result = sp.get_switch_variable_values('p1', 'SN_NOMATCH')
        assert result == {'hostname': 'default-host'}

    def test_falls_back_to_empty_string_when_no_default(self, sp):
        variables = [{'name': 'x', 'switchVariables': []}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        result = sp.get_switch_variable_values('p1', 'SN1')
        assert result == {'x': ''}

    def test_handles_multiple_variables(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                ],
            },
            {
                'name': 'hostname',
                'value': 'default',
                'switchVariables': [],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        result = sp.get_switch_variable_values('p1', 'SN1')
        assert result == {'vlan_id': '200', 'hostname': 'default'}

    def test_returns_empty_dict_when_no_variables(self, sp):
        sp.client.get.return_value = _cli_profile()
        assert sp.get_switch_variable_values('p1', 'SN1') == {}

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_switch_variable_values('p1', 'SN1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_switch_variable_values('p1', 'SN1')


# ── update_switch_variable_values ───────────────────────────────────────────


class TestUpdateSwitchVariableValues:
    """Tests for SwitchProfiles.update_switch_variable_values()."""

    def test_updates_existing_switch_mapping(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                ],
            },
        ]
        profile = _cli_profile(variables=variables)
        # get is called twice: once in update_switch_variable_values, once in get_cli_variables
        sp.client.get.return_value = profile
        sp.client.put.return_value = {}

        sp.update_switch_variable_values('p1', 'SN1', {'vlan_id': '999'})

        put_data = sp.client.put.call_args[1]['data']
        updated_vars = put_data['venueCliTemplate']['variables']
        mapping = updated_vars[0]['switchVariables'][0]
        assert mapping['value'] == '999'

    def test_adds_new_switch_mapping(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_switch_variable_values('p1', 'SN_NEW', {'vlan_id': '500'})

        put_data = sp.client.put.call_args[1]['data']
        updated_vars = put_data['venueCliTemplate']['variables']
        assert len(updated_vars[0]['switchVariables']) == 1
        mapping = updated_vars[0]['switchVariables'][0]
        assert mapping['serialNumbers'] == ['SN_NEW']
        assert mapping['value'] == '500'

    def test_initializes_switch_variables_list_if_missing(self, sp):
        variables = [{'name': 'vlan_id', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_switch_variable_values('p1', 'SN1', {'vlan_id': '42'})

        put_data = sp.client.put.call_args[1]['data']
        updated_vars = put_data['venueCliTemplate']['variables']
        assert 'switchVariables' in updated_vars[0]
        assert updated_vars[0]['switchVariables'][0]['value'] == '42'

    def test_skips_variables_not_in_values_dict(self, sp):
        variables = [
            {'name': 'vlan_id', 'value': '100', 'switchVariables': []},
            {'name': 'hostname', 'value': 'host', 'switchVariables': []},
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_switch_variable_values('p1', 'SN1', {'vlan_id': '42'})

        put_data = sp.client.put.call_args[1]['data']
        updated_vars = put_data['venueCliTemplate']['variables']
        # hostname should have no new switchVariables
        hostname_var = next(v for v in updated_vars if v['name'] == 'hostname')
        assert hostname_var['switchVariables'] == []

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.update_switch_variable_values('p1', 'SN1', {'vlan_id': '1'})

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_switch_variable_values('p1', 'SN1', {'vlan_id': '1'})


# ── get_variable_switch_mappings ────────────────────────────────────────────


class TestGetVariableSwitchMappings:
    """Tests for SwitchProfiles.get_variable_switch_mappings()."""

    def test_returns_flattened_switch_mappings(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1', 'SN2'], 'value': '200', 'id': 'm1'},
                    {'serialNumbers': ['SN3'], 'value': '300', 'id': 'm2'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)

        result = sp.get_variable_switch_mappings('p1', 'vlan_id')

        assert len(result) == 3
        serials = [r['serial'] for r in result]
        assert 'SN1' in serials
        assert 'SN2' in serials
        assert 'SN3' in serials
        sn1 = next(r for r in result if r['serial'] == 'SN1')
        assert sn1['value'] == '200'
        assert sn1['id'] == 'm1'

    def test_returns_empty_list_when_no_switch_variables(self, sp):
        variables = [{'name': 'vlan_id', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        assert sp.get_variable_switch_mappings('p1', 'vlan_id') == []

    def test_raises_resource_not_found_for_unknown_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'other', 'value': '1'}]
        )
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_variable_switch_mappings('p1', 'nonexistent')

    def test_raises_resource_not_found_on_empty_variables(self, sp):
        sp.client.get.return_value = _cli_profile()
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_variable_switch_mappings('p1', 'anything')

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_variable_switch_mappings('p1', 'vlan_id')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_variable_switch_mappings('p1', 'vlan_id')


# ── update_variable_switch_mapping ──────────────────────────────────────────


class TestUpdateVariableSwitchMapping:
    """Tests for SwitchProfiles.update_variable_switch_mapping()."""

    def test_updates_existing_switch_in_variable(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_variable_switch_mapping('p1', 'vlan_id', 'SN1', '999')

        put_data = sp.client.put.call_args[1]['data']
        mapping = put_data['venueCliTemplate']['variables'][0]['switchVariables'][0]
        assert mapping['value'] == '999'

    def test_adds_new_switch_to_variable(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_variable_switch_mapping('p1', 'vlan_id', 'SN_NEW', '500')

        put_data = sp.client.put.call_args[1]['data']
        sv = put_data['venueCliTemplate']['variables'][0]['switchVariables']
        assert len(sv) == 1
        assert sv[0] == {'serialNumbers': ['SN_NEW'], 'value': '500'}

    def test_initializes_switch_variables_if_missing(self, sp):
        variables = [{'name': 'vlan_id', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.update_variable_switch_mapping('p1', 'vlan_id', 'SN1', '42')

        put_data = sp.client.put.call_args[1]['data']
        sv = put_data['venueCliTemplate']['variables'][0]['switchVariables']
        assert len(sv) == 1

    def test_raises_resource_not_found_for_unknown_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'other', 'value': '1'}]
        )
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_variable_switch_mapping('p1', 'nonexistent', 'SN1', 'v')

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.update_variable_switch_mapping('p1', 'vlan_id', 'SN1', 'v')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.update_variable_switch_mapping('p1', 'vlan_id', 'SN1', 'v')


# ── delete_variable_switch_mapping ──────────────────────────────────────────


class TestDeleteVariableSwitchMapping:
    """Tests for SwitchProfiles.delete_variable_switch_mapping()."""

    def test_removes_serial_from_mapping(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1', 'SN2'], 'value': '200'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN1')

        put_data = sp.client.put.call_args[1]['data']
        sv = put_data['venueCliTemplate']['variables'][0]['switchVariables']
        assert len(sv) == 1
        assert sv[0]['serialNumbers'] == ['SN2']

    def test_removes_entire_mapping_when_last_serial(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        sp.client.put.return_value = {}

        sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN1')

        put_data = sp.client.put.call_args[1]['data']
        sv = put_data['venueCliTemplate']['variables'][0]['switchVariables']
        assert sv == []

    def test_raises_resource_not_found_for_unknown_variable(self, sp):
        sp.client.get.return_value = _cli_profile(
            variables=[{'name': 'other', 'value': '1'}]
        )
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.delete_variable_switch_mapping('p1', 'nonexistent', 'SN1')

    def test_raises_resource_not_found_for_unknown_switch(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN_OTHER'], 'value': '200'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)
        with pytest.raises(ResourceNotFoundError, match="Switch.*mapping not found"):
            sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN_MISSING')

    def test_raises_resource_not_found_when_no_switch_variables(self, sp):
        variables = [{'name': 'vlan_id', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        with pytest.raises(ResourceNotFoundError, match="Switch.*mapping not found"):
            sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN1')

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.delete_variable_switch_mapping('p1', 'vlan_id', 'SN1')


# ── get_all_switch_mappings ─────────────────────────────────────────────────


class TestGetAllSwitchMappings:
    """Tests for SwitchProfiles.get_all_switch_mappings()."""

    def test_aggregates_across_variables(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                    {'serialNumbers': ['SN2'], 'value': '300'},
                ],
            },
            {
                'name': 'hostname',
                'value': 'default',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': 'host1'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)

        result = sp.get_all_switch_mappings('p1')

        assert result == {
            'SN1': {'vlan_id': '200', 'hostname': 'host1'},
            'SN2': {'vlan_id': '300'},
        }

    def test_returns_empty_dict_when_no_variables(self, sp):
        sp.client.get.return_value = _cli_profile()
        assert sp.get_all_switch_mappings('p1') == {}

    def test_returns_empty_dict_when_no_switch_variables(self, sp):
        variables = [{'name': 'vlan_id', 'value': '100'}]
        sp.client.get.return_value = _cli_profile(variables=variables)
        assert sp.get_all_switch_mappings('p1') == {}

    def test_handles_multiple_serials_in_one_mapping(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1', 'SN2'], 'value': '200'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)

        result = sp.get_all_switch_mappings('p1')
        assert result == {
            'SN1': {'vlan_id': '200'},
            'SN2': {'vlan_id': '200'},
        }

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_all_switch_mappings('p1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_all_switch_mappings('p1')


# ── get_mapped_switches ────────────────────────────────────────────────────


class TestGetMappedSwitches:
    """Tests for SwitchProfiles.get_mapped_switches()."""

    def test_returns_list_of_switch_serials(self, sp):
        variables = [
            {
                'name': 'vlan_id',
                'value': '100',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': '200'},
                    {'serialNumbers': ['SN2'], 'value': '300'},
                ],
            },
            {
                'name': 'hostname',
                'value': 'default',
                'switchVariables': [
                    {'serialNumbers': ['SN1'], 'value': 'host1'},
                ],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)

        result = sp.get_mapped_switches('p1')
        assert sorted(result) == ['SN1', 'SN2']

    def test_returns_empty_list_when_no_mappings(self, sp):
        sp.client.get.return_value = _cli_profile()
        assert sp.get_mapped_switches('p1') == []

    def test_no_duplicates(self, sp):
        variables = [
            {
                'name': 'v1',
                'value': '1',
                'switchVariables': [{'serialNumbers': ['SN1'], 'value': 'a'}],
            },
            {
                'name': 'v2',
                'value': '2',
                'switchVariables': [{'serialNumbers': ['SN1'], 'value': 'b'}],
            },
        ]
        sp.client.get.return_value = _cli_profile(variables=variables)

        result = sp.get_mapped_switches('p1')
        assert result == ['SN1']

    def test_raises_value_error_for_non_cli_profile(self, sp):
        sp.client.get.return_value = _non_cli_profile()
        with pytest.raises(ValueError, match="not a CLI profile"):
            sp.get_mapped_switches('p1')

    def test_propagates_resource_not_found_error(self, sp):
        sp.client.get.side_effect = ResourceNotFoundError(message="not found")
        with pytest.raises(ResourceNotFoundError, match="not found"):
            sp.get_mapped_switches('p1')
