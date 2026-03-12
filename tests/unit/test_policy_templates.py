"""Unit tests for the PolicyTemplates module."""

import json
from unittest.mock import MagicMock, call

import pytest

from r1_sdk.modules.policy_templates import PolicyTemplates


@pytest.fixture
def policy_templates(mock_client):
    """Create a PolicyTemplates instance backed by a mock client."""
    return PolicyTemplates(mock_client)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestInit:
    def test_stores_client_reference(self, mock_client):
        pt = PolicyTemplates(mock_client)
        assert pt.client is mock_client


# ---------------------------------------------------------------------------
# query_templates()
# ---------------------------------------------------------------------------

class TestQueryTemplates:
    def test_posts_to_query_endpoint(self, policy_templates):
        policy_templates.client.post.return_value = {"data": []}
        policy_templates.query_templates()
        policy_templates.client.post.assert_called_once_with(
            "/policyTemplates/query", data={}
        )

    def test_passes_filters(self, policy_templates):
        policy_templates.client.post.return_value = {"data": []}
        policy_templates.query_templates({"page": 0, "pageSize": 10})
        call_data = policy_templates.client.post.call_args[1]["data"]
        assert call_data["page"] == 0
        assert call_data["pageSize"] == 10

    def test_returns_api_response(self, policy_templates):
        expected = {"data": [{"id": 1}], "totalCount": 1}
        policy_templates.client.post.return_value = expected
        assert policy_templates.query_templates() == expected


# ---------------------------------------------------------------------------
# list_all_templates()
# ---------------------------------------------------------------------------

class TestListAllTemplates:
    def test_delegates_to_paginate_query(self, policy_templates):
        policy_templates.client.paginate_query.return_value = [{"id": 1}]
        result = policy_templates.list_all_templates()
        policy_templates.client.paginate_query.assert_called_once_with(
            "/policyTemplates/query", None
        )
        assert result == [{"id": 1}]

    def test_passes_kwargs(self, policy_templates):
        policy_templates.client.paginate_query.return_value = []
        policy_templates.list_all_templates(ruleType="RADIUS")
        call_data = policy_templates.client.paginate_query.call_args[0][1]
        assert call_data["ruleType"] == "RADIUS"


# ---------------------------------------------------------------------------
# get_template()
# ---------------------------------------------------------------------------

class TestGetTemplate:
    def test_calls_get_with_int_id(self, policy_templates):
        policy_templates.client.get.return_value = {"id": 42}
        policy_templates.get_template(42)
        policy_templates.client.get.assert_called_once_with("/policyTemplates/42")

    def test_returns_template_data(self, policy_templates):
        expected = {"id": 42, "name": "RADIUS"}
        policy_templates.client.get.return_value = expected
        assert policy_templates.get_template(42) == expected


# ---------------------------------------------------------------------------
# create_policy()
# ---------------------------------------------------------------------------

class TestCreatePolicy:
    def test_posts_with_sync_header(self, policy_templates):
        policy_templates.client.request.return_value = {"id": "pol-uuid"}
        policy_templates.create_policy(42, "TestPolicy", "RADIUS")

        policy_templates.client.request.assert_called_once()
        args, kwargs = policy_templates.client.request.call_args
        assert args[0] == "POST"
        assert args[1] == "/policyTemplates/42/policies"
        assert kwargs["headers"]["Content-Type"] == "application/ruckus.one.v1-synchronous+json"

    def test_body_contains_required_fields(self, policy_templates):
        policy_templates.client.request.return_value = {"id": "pol-uuid"}
        policy_templates.create_policy(42, "TestPolicy", "RADIUS")

        _, kwargs = policy_templates.client.request.call_args
        body = json.loads(kwargs["data"])
        assert body["name"] == "TestPolicy"
        assert body["policyType"] == "RADIUS"

    def test_body_includes_optional_fields(self, policy_templates):
        policy_templates.client.request.return_value = {"id": "pol-uuid"}
        policy_templates.create_policy(
            42, "TestPolicy", "RADIUS",
            description="A test policy",
            on_match_response="rag-uuid"
        )

        _, kwargs = policy_templates.client.request.call_args
        body = json.loads(kwargs["data"])
        assert body["description"] == "A test policy"
        assert body["onMatchResponse"] == "rag-uuid"

    def test_none_optional_fields_omitted(self, policy_templates):
        policy_templates.client.request.return_value = {"id": "pol-uuid"}
        policy_templates.create_policy(42, "TestPolicy", "RADIUS")

        _, kwargs = policy_templates.client.request.call_args
        body = json.loads(kwargs["data"])
        assert "description" not in body
        assert "onMatchResponse" not in body

    def test_returns_created_policy(self, policy_templates):
        expected = {"id": "pol-uuid", "name": "TestPolicy"}
        policy_templates.client.request.return_value = expected
        result = policy_templates.create_policy(42, "TestPolicy", "RADIUS")
        assert result == expected


# ---------------------------------------------------------------------------
# get_policy()
# ---------------------------------------------------------------------------

class TestGetPolicy:
    def test_calls_get_with_int_template_and_string_policy(self, policy_templates):
        policy_templates.client.get.return_value = {"id": "pol-uuid"}
        policy_templates.get_policy(42, "pol-uuid")
        policy_templates.client.get.assert_called_once_with(
            "/policyTemplates/42/policies/pol-uuid"
        )

    def test_returns_policy_data(self, policy_templates):
        expected = {"id": "pol-uuid", "name": "MyPolicy"}
        policy_templates.client.get.return_value = expected
        assert policy_templates.get_policy(42, "pol-uuid") == expected


# ---------------------------------------------------------------------------
# delete_policy()
# ---------------------------------------------------------------------------

class TestDeletePolicy:
    def test_calls_delete_with_correct_path(self, policy_templates):
        policy_templates.delete_policy(42, "pol-uuid")
        policy_templates.client.delete.assert_called_once_with(
            "/policyTemplates/42/policies/pol-uuid"
        )

    def test_returns_none(self, policy_templates):
        policy_templates.client.delete.return_value = None
        result = policy_templates.delete_policy(42, "pol-uuid")
        assert result is None
