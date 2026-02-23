"""Unit tests for the IdentityGroups module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.identity_groups import IdentityGroups


@pytest.fixture
def identity_groups(mock_client):
    """Create an IdentityGroups instance backed by a mock client."""
    return IdentityGroups(mock_client)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestInit:
    def test_stores_client_reference(self, mock_client):
        ig = IdentityGroups(mock_client)
        assert ig.client is mock_client


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------

class TestList:
    def test_calls_get_identity_groups(self, identity_groups):
        identity_groups.client.get.return_value = []
        identity_groups.list()
        identity_groups.client.get.assert_called_once_with("/identityGroups")

    def test_returns_api_response(self, identity_groups):
        expected = [{"id": "g1", "name": "Staff"}]
        identity_groups.client.get.return_value = expected
        result = identity_groups.list()
        assert result == expected

    def test_propagates_exception(self, identity_groups):
        identity_groups.client.get.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            identity_groups.list()


# ---------------------------------------------------------------------------
# query()
# ---------------------------------------------------------------------------

class TestQuery:
    def test_posts_to_query_endpoint(self, identity_groups):
        identity_groups.client.post.return_value = {"data": []}
        identity_groups.query()
        identity_groups.client.post.assert_called_once_with(
            "/identityGroups/query",
            data={"page": 0, "size": 20},
        )

    def test_default_pagination(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query()
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["page"] == 0
        assert call_data["size"] == 20

    def test_custom_pagination(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(page=3, page_size=50)
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["page"] == 3
        assert call_data["size"] == 50

    def test_certificate_template_id_filter(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(certificate_template_id="ct-1")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["certificateTemplateId"] == "ct-1"

    def test_dpsk_pool_id_filter(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(dpsk_pool_id="dp-1")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["dpskPoolId"] == "dp-1"

    def test_policy_set_id_filter(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(policy_set_id="ps-1")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["policySetId"] == "ps-1"

    def test_property_id_filter(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(property_id="prop-1")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["propertyId"] == "prop-1"

    def test_all_filters_combined(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(
            page=1,
            page_size=10,
            certificate_template_id="ct-1",
            dpsk_pool_id="dp-1",
            policy_set_id="ps-1",
            property_id="prop-1",
        )
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data == {
            "page": 1,
            "size": 10,
            "certificateTemplateId": "ct-1",
            "dpskPoolId": "dp-1",
            "policySetId": "ps-1",
            "propertyId": "prop-1",
        }

    def test_extra_kwargs_forwarded(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.query(customField="val")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["customField"] == "val"

    def test_none_filters_omitted(self, identity_groups):
        """Optional filters that are None should not appear in the payload."""
        identity_groups.client.post.return_value = {}
        identity_groups.query()
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert "certificateTemplateId" not in call_data
        assert "dpskPoolId" not in call_data
        assert "policySetId" not in call_data
        assert "propertyId" not in call_data

    def test_returns_api_response(self, identity_groups):
        expected = {"data": [{"id": "g1"}], "totalCount": 1}
        identity_groups.client.post.return_value = expected
        assert identity_groups.query() == expected

    def test_propagates_exception(self, identity_groups):
        identity_groups.client.post.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="fail"):
            identity_groups.query()


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_calls_get_with_group_id(self, identity_groups):
        identity_groups.client.get.return_value = {"id": "g1"}
        identity_groups.get("g1")
        identity_groups.client.get.assert_called_once_with("/identityGroups/g1")

    def test_returns_group_data(self, identity_groups):
        expected = {"id": "g1", "name": "Employees"}
        identity_groups.client.get.return_value = expected
        assert identity_groups.get("g1") == expected

    def test_raises_resource_not_found_on_404(self, identity_groups):
        identity_groups.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.get("missing-id")
        assert "missing-id" in str(exc_info.value)

    def test_resource_not_found_preserves_404_status(self, identity_groups):
        identity_groups.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.get("bad-id")
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestCreate:
    def test_posts_with_name_only(self, identity_groups):
        identity_groups.client.post.return_value = {"id": "new-1"}
        identity_groups.create("Guests")
        identity_groups.client.post.assert_called_once_with(
            "/identityGroups",
            data={"name": "Guests"},
        )

    def test_posts_with_all_optional_fields(self, identity_groups):
        identity_groups.client.post.return_value = {"id": "new-2"}
        identity_groups.create(
            name="Full",
            description="All fields",
            dpsk_pool_id="dp-1",
            certificate_template_id="ct-1",
            policy_set_id="ps-1",
            property_id="prop-1",
        )
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data == {
            "name": "Full",
            "description": "All fields",
            "dpskPoolId": "dp-1",
            "certificateTemplateId": "ct-1",
            "policySetId": "ps-1",
            "propertyId": "prop-1",
        }

    def test_extra_kwargs_included(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.create("Group", customAttr="abc")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert call_data["customAttr"] == "abc"

    def test_none_optional_fields_omitted(self, identity_groups):
        identity_groups.client.post.return_value = {}
        identity_groups.create("Minimal")
        call_data = identity_groups.client.post.call_args[1]["data"]
        assert "description" not in call_data
        assert "dpskPoolId" not in call_data
        assert "certificateTemplateId" not in call_data
        assert "policySetId" not in call_data
        assert "propertyId" not in call_data

    def test_returns_created_group(self, identity_groups):
        expected = {"id": "new-1", "name": "Guests"}
        identity_groups.client.post.return_value = expected
        assert identity_groups.create("Guests") == expected


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_puts_with_group_id(self, identity_groups):
        identity_groups.client.put.return_value = {"id": "g1"}
        identity_groups.update("g1", name="Renamed")
        identity_groups.client.put.assert_called_once_with(
            "/identityGroups/g1",
            data={"name": "Renamed"},
        )

    def test_forwards_all_kwargs(self, identity_groups):
        identity_groups.client.put.return_value = {}
        identity_groups.update("g1", name="New", description="Desc", custom="val")
        call_data = identity_groups.client.put.call_args[1]["data"]
        assert call_data == {"name": "New", "description": "Desc", "custom": "val"}

    def test_returns_updated_group(self, identity_groups):
        expected = {"id": "g1", "name": "Renamed"}
        identity_groups.client.put.return_value = expected
        assert identity_groups.update("g1", name="Renamed") == expected

    def test_raises_resource_not_found_on_404(self, identity_groups):
        identity_groups.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.update("missing", name="x")
        assert "missing" in str(exc_info.value)

    def test_empty_kwargs_sends_empty_dict(self, identity_groups):
        identity_groups.client.put.return_value = {}
        identity_groups.update("g1")
        call_data = identity_groups.client.put.call_args[1]["data"]
        assert call_data == {}


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    def test_calls_delete_with_group_id(self, identity_groups):
        identity_groups.delete("g1")
        identity_groups.client.delete.assert_called_once_with("/identityGroups/g1")

    def test_returns_none(self, identity_groups):
        identity_groups.client.delete.return_value = None
        result = identity_groups.delete("g1")
        assert result is None

    def test_raises_resource_not_found_on_404(self, identity_groups):
        identity_groups.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.delete("gone")
        assert "gone" in str(exc_info.value)


# ---------------------------------------------------------------------------
# associate_dpsk_pool()
# ---------------------------------------------------------------------------

class TestAssociateDpskPool:
    def test_puts_correct_url(self, identity_groups):
        identity_groups.client.put.return_value = {}
        identity_groups.associate_dpsk_pool("g1", "dp-1")
        identity_groups.client.put.assert_called_once_with(
            "/identityGroups/g1/dpskPools/dp-1"
        )

    def test_no_data_payload(self, identity_groups):
        """associate_dpsk_pool should not send a data payload."""
        identity_groups.client.put.return_value = {}
        identity_groups.associate_dpsk_pool("g1", "dp-1")
        args, kwargs = identity_groups.client.put.call_args
        assert "data" not in kwargs

    def test_returns_api_response(self, identity_groups):
        expected = {"status": "ok"}
        identity_groups.client.put.return_value = expected
        assert identity_groups.associate_dpsk_pool("g1", "dp-1") == expected

    def test_raises_resource_not_found_on_404(self, identity_groups):
        identity_groups.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.associate_dpsk_pool("bad-g", "dp-1")
        assert "bad-g" in str(exc_info.value)


# ---------------------------------------------------------------------------
# associate_policy_set()
# ---------------------------------------------------------------------------

class TestAssociatePolicySet:
    def test_puts_correct_url(self, identity_groups):
        identity_groups.client.put.return_value = {}
        identity_groups.associate_policy_set("g1", "ps-1")
        identity_groups.client.put.assert_called_once_with(
            "/identityGroups/g1/policySets/ps-1"
        )

    def test_no_data_payload(self, identity_groups):
        """associate_policy_set should not send a data payload."""
        identity_groups.client.put.return_value = {}
        identity_groups.associate_policy_set("g1", "ps-1")
        args, kwargs = identity_groups.client.put.call_args
        assert "data" not in kwargs

    def test_returns_api_response(self, identity_groups):
        expected = {"status": "associated"}
        identity_groups.client.put.return_value = expected
        assert identity_groups.associate_policy_set("g1", "ps-1") == expected

    def test_raises_resource_not_found_on_404(self, identity_groups):
        identity_groups.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identity_groups.associate_policy_set("bad-g", "ps-1")
        assert "bad-g" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Removed methods should NOT exist
# ---------------------------------------------------------------------------

class TestRemovedMethods:
    def test_no_get_identity_method(self, identity_groups):
        assert not hasattr(identity_groups, "get_identity")

    def test_no_create_identity_method(self, identity_groups):
        assert not hasattr(identity_groups, "create_identity")


# ── list_all ─────────────────────────────────────────────────────────────


class TestListAll:
    """Tests for IdentityGroups.list_all()."""

    def test_delegates_to_paginate_query(self, identity_groups):
        identity_groups.client.paginate_query.return_value = [{"id": "g1"}]
        result = identity_groups.list_all()
        identity_groups.client.paginate_query.assert_called_once_with(
            "/identityGroups/query", {}
        )
        assert result == [{"id": "g1"}]

    def test_passes_kwargs(self, identity_groups):
        identity_groups.client.paginate_query.return_value = []
        identity_groups.list_all(dpskPoolId="pool-1")
        call_data = identity_groups.client.paginate_query.call_args[0][1]
        assert call_data["dpskPoolId"] == "pool-1"
