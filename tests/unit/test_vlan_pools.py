"""Comprehensive unit tests for the VLANPools module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.vlan_pools import VLANPools


@pytest.fixture
def vlan_pools():
    client = MagicMock()
    return VLANPools(client)


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

class TestInit:
    def test_stores_client_reference(self, vlan_pools):
        assert vlan_pools.client is not None

    def test_client_is_mock(self, vlan_pools):
        assert isinstance(vlan_pools.client, MagicMock)


# ---------------------------------------------------------------------------
# list_pools
# ---------------------------------------------------------------------------

class TestListPools:
    def test_posts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.list_pools()
        vlan_pools.client.post.assert_called_once()
        args, kwargs = vlan_pools.client.post.call_args
        assert args[0] == "/vlanPools/query"

    def test_default_query_data(self, vlan_pools):
        vlan_pools.list_pools()
        _, kwargs = vlan_pools.client.post.call_args
        expected = {"pageSize": 100, "page": 0, "sortOrder": "ASC"}
        assert kwargs["data"] == expected

    def test_custom_query_data_passed_through(self, vlan_pools):
        custom = {"pageSize": 50, "page": 2, "sortOrder": "DESC"}
        vlan_pools.list_pools(query_data=custom)
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["pageSize"] == 50
        assert kwargs["data"]["page"] == 2
        assert kwargs["data"]["sortOrder"] == "DESC"

    def test_sort_order_uppercased(self, vlan_pools):
        vlan_pools.list_pools(query_data={"sortOrder": "asc"})
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["sortOrder"] == "ASC"

    def test_returns_client_response(self, vlan_pools):
        vlan_pools.client.post.return_value = {"data": [], "totalCount": 0}
        result = vlan_pools.list_pools()
        assert result == {"data": [], "totalCount": 0}

    def test_propagates_exception(self, vlan_pools):
        vlan_pools.client.post.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            vlan_pools.list_pools()

    def test_query_without_sort_order_key(self, vlan_pools):
        """Custom query that omits sortOrder should not raise."""
        vlan_pools.list_pools(query_data={"pageSize": 10})
        _, kwargs = vlan_pools.client.post.call_args
        assert "sortOrder" not in kwargs["data"]


# ---------------------------------------------------------------------------
# get_vlan_pool
# ---------------------------------------------------------------------------

class TestGetVlanPool:
    def test_gets_correct_endpoint(self, vlan_pools):
        vlan_pools.get_vlan_pool("pool-123")
        vlan_pools.client.get.assert_called_once_with("/vlanPools/pool-123")

    def test_returns_pool_data(self, vlan_pools):
        expected = {"id": "pool-123", "name": "Corp"}
        vlan_pools.client.get.return_value = expected
        assert vlan_pools.get_vlan_pool("pool-123") == expected

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool with ID pool-xyz not found"):
            vlan_pools.get_vlan_pool("pool-xyz")

    def test_404_message_contains_id(self, vlan_pools):
        vlan_pools.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            vlan_pools.get_vlan_pool("abc-999")
        assert "abc-999" in str(exc_info.value)


# ---------------------------------------------------------------------------
# create_vlan_pool
# ---------------------------------------------------------------------------

class TestCreateVlanPool:
    def test_posts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.create_vlan_pool("TestPool", [{"vlanId": 100}])
        args, kwargs = vlan_pools.client.post.call_args
        assert args[0] == "/vlanPools"

    def test_required_fields_in_payload(self, vlan_pools):
        vlans = [{"vlanId": 100}, {"vlanId": 200}]
        vlan_pools.create_vlan_pool("MyPool", vlans)
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["name"] == "MyPool"
        assert kwargs["data"]["vlans"] == vlans

    def test_description_included_when_provided(self, vlan_pools):
        vlan_pools.create_vlan_pool("P", [{"vlanId": 1}], description="A pool")
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["description"] == "A pool"

    def test_description_absent_when_none(self, vlan_pools):
        vlan_pools.create_vlan_pool("P", [{"vlanId": 1}])
        _, kwargs = vlan_pools.client.post.call_args
        assert "description" not in kwargs["data"]

    def test_description_absent_when_empty_string(self, vlan_pools):
        """Empty string is falsy, so description should not be added."""
        vlan_pools.create_vlan_pool("P", [{"vlanId": 1}], description="")
        _, kwargs = vlan_pools.client.post.call_args
        assert "description" not in kwargs["data"]

    def test_kwargs_merged_into_payload(self, vlan_pools):
        vlan_pools.create_vlan_pool("P", [{"vlanId": 1}], tenantId="t-1", custom="val")
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["tenantId"] == "t-1"
        assert kwargs["data"]["custom"] == "val"

    def test_returns_created_pool(self, vlan_pools):
        vlan_pools.client.post.return_value = {"id": "new-pool", "name": "P"}
        result = vlan_pools.create_vlan_pool("P", [])
        assert result["id"] == "new-pool"


# ---------------------------------------------------------------------------
# update_vlan_pool
# ---------------------------------------------------------------------------

class TestUpdateVlanPool:
    def test_puts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.update_vlan_pool("pool-1", name="Updated")
        args, kwargs = vlan_pools.client.put.call_args
        assert args[0] == "/vlanPools/pool-1"

    def test_kwargs_sent_as_data(self, vlan_pools):
        vlan_pools.update_vlan_pool("pool-1", name="New", description="Desc")
        _, kwargs = vlan_pools.client.put.call_args
        assert kwargs["data"] == {"name": "New", "description": "Desc"}

    def test_returns_updated_pool(self, vlan_pools):
        vlan_pools.client.put.return_value = {"id": "pool-1", "name": "New"}
        result = vlan_pools.update_vlan_pool("pool-1", name="New")
        assert result["name"] == "New"

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool with ID pool-bad not found"):
            vlan_pools.update_vlan_pool("pool-bad", name="X")

    def test_empty_kwargs(self, vlan_pools):
        """Calling with no kwargs should still PUT with an empty dict."""
        vlan_pools.update_vlan_pool("pool-1")
        _, kwargs = vlan_pools.client.put.call_args
        assert kwargs["data"] == {}


# ---------------------------------------------------------------------------
# delete_vlan_pool
# ---------------------------------------------------------------------------

class TestDeleteVlanPool:
    def test_deletes_correct_endpoint(self, vlan_pools):
        vlan_pools.delete_vlan_pool("pool-del")
        vlan_pools.client.delete.assert_called_once_with("/vlanPools/pool-del")

    def test_returns_none(self, vlan_pools):
        vlan_pools.client.delete.return_value = None
        result = vlan_pools.delete_vlan_pool("pool-del")
        assert result is None

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool with ID pool-gone not found"):
            vlan_pools.delete_vlan_pool("pool-gone")


# ---------------------------------------------------------------------------
# list_profiles
# ---------------------------------------------------------------------------

class TestListProfiles:
    def test_posts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.list_profiles()
        args, kwargs = vlan_pools.client.post.call_args
        assert args[0] == "/vlanPoolProfiles/query"

    def test_default_query_data(self, vlan_pools):
        vlan_pools.list_profiles()
        _, kwargs = vlan_pools.client.post.call_args
        expected = {"pageSize": 100, "page": 0, "sortOrder": "ASC"}
        assert kwargs["data"] == expected

    def test_custom_query_data(self, vlan_pools):
        custom = {"pageSize": 25, "page": 1, "sortOrder": "DESC", "filters": []}
        vlan_pools.list_profiles(query_data=custom)
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["pageSize"] == 25
        assert kwargs["data"]["sortOrder"] == "DESC"
        assert kwargs["data"]["filters"] == []

    def test_sort_order_uppercased(self, vlan_pools):
        vlan_pools.list_profiles(query_data={"sortOrder": "desc"})
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["sortOrder"] == "DESC"

    def test_returns_client_response(self, vlan_pools):
        vlan_pools.client.post.return_value = {"data": [{"id": "p1"}], "totalCount": 1}
        result = vlan_pools.list_profiles()
        assert result["totalCount"] == 1

    def test_propagates_exception(self, vlan_pools):
        vlan_pools.client.post.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="fail"):
            vlan_pools.list_profiles()

    def test_query_without_sort_order_key(self, vlan_pools):
        vlan_pools.list_profiles(query_data={"pageSize": 5})
        _, kwargs = vlan_pools.client.post.call_args
        assert "sortOrder" not in kwargs["data"]


# ---------------------------------------------------------------------------
# get_vlan_pool_profile
# ---------------------------------------------------------------------------

class TestGetVlanPoolProfile:
    def test_gets_correct_endpoint(self, vlan_pools):
        vlan_pools.get_vlan_pool_profile("prof-1")
        vlan_pools.client.get.assert_called_once_with("/vlanPoolProfiles/prof-1")

    def test_returns_profile_data(self, vlan_pools):
        expected = {"id": "prof-1", "name": "Default"}
        vlan_pools.client.get.return_value = expected
        assert vlan_pools.get_vlan_pool_profile("prof-1") == expected

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool profile with ID prof-bad not found"):
            vlan_pools.get_vlan_pool_profile("prof-bad")

    def test_404_message_contains_id(self, vlan_pools):
        vlan_pools.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            vlan_pools.get_vlan_pool_profile("prof-xyz")
        assert "prof-xyz" in str(exc_info.value)


# ---------------------------------------------------------------------------
# create_vlan_pool_profile
# ---------------------------------------------------------------------------

class TestCreateVlanPoolProfile:
    def test_posts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("Prof1", "pool-1")
        args, kwargs = vlan_pools.client.post.call_args
        assert args[0] == "/vlanPoolProfiles"

    def test_required_fields_in_payload(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("Prof1", "pool-1")
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["name"] == "Prof1"
        assert kwargs["data"]["vlanPoolId"] == "pool-1"

    def test_description_included_when_provided(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("P", "pool-1", description="Desc")
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["description"] == "Desc"

    def test_description_absent_when_none(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("P", "pool-1")
        _, kwargs = vlan_pools.client.post.call_args
        assert "description" not in kwargs["data"]

    def test_description_absent_when_empty_string(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("P", "pool-1", description="")
        _, kwargs = vlan_pools.client.post.call_args
        assert "description" not in kwargs["data"]

    def test_kwargs_merged_into_payload(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile("P", "pool-1", priority=5, enabled=True)
        _, kwargs = vlan_pools.client.post.call_args
        assert kwargs["data"]["priority"] == 5
        assert kwargs["data"]["enabled"] is True

    def test_returns_created_profile(self, vlan_pools):
        vlan_pools.client.post.return_value = {"id": "prof-new", "name": "P"}
        result = vlan_pools.create_vlan_pool_profile("P", "pool-1")
        assert result["id"] == "prof-new"


# ---------------------------------------------------------------------------
# update_vlan_pool_profile
# ---------------------------------------------------------------------------

class TestUpdateVlanPoolProfile:
    def test_puts_to_correct_endpoint(self, vlan_pools):
        vlan_pools.update_vlan_pool_profile("prof-1", name="Updated")
        args, kwargs = vlan_pools.client.put.call_args
        assert args[0] == "/vlanPoolProfiles/prof-1"

    def test_kwargs_sent_as_data(self, vlan_pools):
        vlan_pools.update_vlan_pool_profile("prof-1", name="New", vlanPoolId="pool-2")
        _, kwargs = vlan_pools.client.put.call_args
        assert kwargs["data"] == {"name": "New", "vlanPoolId": "pool-2"}

    def test_returns_updated_profile(self, vlan_pools):
        vlan_pools.client.put.return_value = {"id": "prof-1", "name": "New"}
        result = vlan_pools.update_vlan_pool_profile("prof-1", name="New")
        assert result["name"] == "New"

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool profile with ID prof-bad not found"):
            vlan_pools.update_vlan_pool_profile("prof-bad", name="X")

    def test_empty_kwargs(self, vlan_pools):
        vlan_pools.update_vlan_pool_profile("prof-1")
        _, kwargs = vlan_pools.client.put.call_args
        assert kwargs["data"] == {}


# ---------------------------------------------------------------------------
# delete_vlan_pool_profile
# ---------------------------------------------------------------------------

class TestDeleteVlanPoolProfile:
    def test_deletes_correct_endpoint(self, vlan_pools):
        vlan_pools.delete_vlan_pool_profile("prof-del")
        vlan_pools.client.delete.assert_called_once_with("/vlanPoolProfiles/prof-del")

    def test_returns_none(self, vlan_pools):
        vlan_pools.client.delete.return_value = None
        result = vlan_pools.delete_vlan_pool_profile("prof-del")
        assert result is None

    def test_404_raises_resource_not_found(self, vlan_pools):
        vlan_pools.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="VLAN pool profile with ID prof-gone not found"):
            vlan_pools.delete_vlan_pool_profile("prof-gone")


# ---------------------------------------------------------------------------
# Cross-cutting / edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_pool_and_profile_use_separate_endpoints(self, vlan_pools):
        """Ensure pool and profile operations hit different base paths."""
        vlan_pools.client.get.return_value = {}
        vlan_pools.get_vlan_pool("id-1")
        vlan_pools.get_vlan_pool_profile("id-1")
        calls = vlan_pools.client.get.call_args_list
        assert calls[0] == call("/vlanPools/id-1")
        assert calls[1] == call("/vlanPoolProfiles/id-1")

    def test_list_pools_and_profiles_use_separate_endpoints(self, vlan_pools):
        vlan_pools.list_pools()
        vlan_pools.list_profiles()
        calls = vlan_pools.client.post.call_args_list
        assert calls[0][0][0] == "/vlanPools/query"
        assert calls[1][0][0] == "/vlanPoolProfiles/query"

    def test_resource_not_found_has_404_status(self, vlan_pools):
        vlan_pools.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            vlan_pools.get_vlan_pool("missing")
        assert exc_info.value.status_code == 404

    def test_non_404_exceptions_propagate_unchanged(self, vlan_pools):
        """Non-ResourceNotFoundError exceptions should not be caught."""
        vlan_pools.client.get.side_effect = ValueError("unexpected")
        with pytest.raises(ValueError, match="unexpected"):
            vlan_pools.get_vlan_pool("any-id")

    def test_create_pool_with_description_and_kwargs(self, vlan_pools):
        """Description and kwargs should all appear in final payload."""
        vlan_pools.create_vlan_pool(
            "Full", [{"vlanId": 10}], description="Full pool", tenantId="t-1"
        )
        _, kwargs = vlan_pools.client.post.call_args
        data = kwargs["data"]
        assert data["name"] == "Full"
        assert data["vlans"] == [{"vlanId": 10}]
        assert data["description"] == "Full pool"
        assert data["tenantId"] == "t-1"

    def test_create_profile_with_description_and_kwargs(self, vlan_pools):
        vlan_pools.create_vlan_pool_profile(
            "FullProf", "pool-1", description="Full prof", priority=1
        )
        _, kwargs = vlan_pools.client.post.call_args
        data = kwargs["data"]
        assert data["name"] == "FullProf"
        assert data["vlanPoolId"] == "pool-1"
        assert data["description"] == "Full prof"
        assert data["priority"] == 1
