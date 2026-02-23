"""Comprehensive unit tests for the L3AclPolicies module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.l3_acl_policies import L3AclPolicies, MAX_L3ACL_RULES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def l3acl():
    """Create an L3AclPolicies instance backed by a mock client."""
    client = MagicMock()
    return L3AclPolicies(client)


@pytest.fixture
def sample_rule():
    """A minimal valid rule dict for reuse across tests."""
    return {
        "description": "Allow HTTP",
        "priority": 1,
        "access": "ALLOW",
        "source": {"enableIpSubnet": False},
        "destination": {"enableIpSubnet": False},
    }


# ===================================================================
# list()
# ===================================================================

class TestList:
    """Tests for L3AclPolicies.list()."""

    def test_list_default_query(self, l3acl):
        """list() with no args POSTs the default query body."""
        l3acl.client.post.return_value = {"data": [], "totalCount": 0}

        result = l3acl.list()

        l3acl.client.post.assert_called_once_with(
            "/l3AclPolicies/query",
            data={"pageSize": 100, "page": 0, "sortOrder": "ASC"},
        )
        assert result == {"data": [], "totalCount": 0}

    def test_list_custom_query(self, l3acl):
        """list() forwards a caller-supplied query body."""
        custom_query = {"pageSize": 50, "page": 2, "sortOrder": "DESC"}
        l3acl.client.post.return_value = {"data": [{"id": "p1"}], "totalCount": 1}

        result = l3acl.list(query_data=custom_query)

        l3acl.client.post.assert_called_once_with(
            "/l3AclPolicies/query",
            data=custom_query,
        )
        assert result["totalCount"] == 1

    def test_list_sort_order_uppercased(self, l3acl):
        """list() normalises sortOrder to uppercase."""
        l3acl.client.post.return_value = {}

        l3acl.list(query_data={"sortOrder": "desc"})

        call_data = l3acl.client.post.call_args[1]["data"] if l3acl.client.post.call_args[1] else l3acl.client.post.call_args[0][1]
        # The positional arg is data= in the call
        actual_data = l3acl.client.post.call_args
        assert actual_data[1]["data"]["sortOrder"] == "DESC" or actual_data[0][1]["sortOrder"] == "DESC"

    def test_list_propagates_exception(self, l3acl):
        """list() lets unexpected errors bubble up."""
        l3acl.client.post.side_effect = RuntimeError("connection lost")

        with pytest.raises(RuntimeError, match="connection lost"):
            l3acl.list()


# ===================================================================
# get()
# ===================================================================

class TestGet:
    """Tests for L3AclPolicies.get()."""

    def test_get_returns_policy(self, l3acl):
        """get() returns the policy dict from the API."""
        expected = {"id": "abc-123", "name": "My Policy"}
        l3acl.client.get.return_value = expected

        result = l3acl.get("abc-123")

        l3acl.client.get.assert_called_once_with("/l3AclPolicies/abc-123")
        assert result == expected

    def test_get_not_found_raises(self, l3acl):
        """get() raises ResourceNotFoundError with a descriptive message on 404."""
        l3acl.client.get.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="abc-123"):
            l3acl.get("abc-123")

    def test_get_other_exception_propagates(self, l3acl):
        """get() does not swallow non-404 exceptions."""
        l3acl.client.get.side_effect = ValueError("bad value")

        with pytest.raises(ValueError, match="bad value"):
            l3acl.get("abc-123")


# ===================================================================
# create()
# ===================================================================

class TestCreate:
    """Tests for L3AclPolicies.create()."""

    def test_create_minimal(self, l3acl, sample_rule):
        """create() POSTs correct payload with required args only."""
        l3acl.client.post.return_value = {"requestId": "r1"}

        result = l3acl.create(name="Block All", l3_rules=[sample_rule])

        l3acl.client.post.assert_called_once()
        call_args = l3acl.client.post.call_args
        data = call_args[1]["data"] if "data" in (call_args[1] or {}) else call_args[0][1]
        assert data["name"] == "Block All"
        assert data["l3Rules"] == [sample_rule]
        assert data["defaultAccess"] == "BLOCK"
        assert "description" not in data
        assert result == {"requestId": "r1"}

    def test_create_with_description(self, l3acl, sample_rule):
        """create() includes description when provided."""
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=[sample_rule], description="My policy")

        data = l3acl.client.post.call_args[1].get("data") or l3acl.client.post.call_args[0][1]
        assert data["description"] == "My policy"

    def test_create_default_access_uppercased(self, l3acl, sample_rule):
        """create() uppercases the default_access value."""
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=[sample_rule], default_access="allow")

        data = l3acl.client.post.call_args[1].get("data") or l3acl.client.post.call_args[0][1]
        assert data["defaultAccess"] == "ALLOW"

    def test_create_kwargs_merged(self, l3acl, sample_rule):
        """create() merges extra kwargs into the payload."""
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=[sample_rule], tenantId="t1")

        data = l3acl.client.post.call_args[1].get("data") or l3acl.client.post.call_args[0][1]
        assert data["tenantId"] == "t1"

    def test_create_posts_to_correct_endpoint(self, l3acl, sample_rule):
        """create() targets /l3AclPolicies."""
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=[sample_rule])

        endpoint = l3acl.client.post.call_args[0][0]
        assert endpoint == "/l3AclPolicies"

    # --- validation: rule count ---

    def test_create_rejects_too_many_rules(self, l3acl):
        """create() raises ValueError when rules exceed MAX_L3ACL_RULES (128)."""
        rules = [{"priority": i, "description": f"r{i}"} for i in range(1, MAX_L3ACL_RULES + 2)]
        assert len(rules) == 129

        with pytest.raises(ValueError, match="Too many L3 rules"):
            l3acl.create(name="P", l3_rules=rules)

        l3acl.client.post.assert_not_called()

    def test_create_accepts_max_rules(self, l3acl):
        """create() accepts exactly MAX_L3ACL_RULES rules."""
        rules = [{"priority": i, "description": f"r{i}"} for i in range(1, MAX_L3ACL_RULES + 1)]
        assert len(rules) == 128
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=rules)  # should not raise

        l3acl.client.post.assert_called_once()

    # --- validation: rule priority ---

    def test_create_rejects_priority_over_max(self, l3acl):
        """create() raises ValueError if any rule priority exceeds 128."""
        rules = [{"priority": 200, "description": "bad"}]

        with pytest.raises(ValueError, match="priority 200 exceeds maximum"):
            l3acl.create(name="P", l3_rules=rules)

        l3acl.client.post.assert_not_called()

    def test_create_accepts_priority_at_max(self, l3acl):
        """create() accepts a rule with priority == 128."""
        rules = [{"priority": 128, "description": "ok"}]
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=rules)  # should not raise

    def test_create_skips_priority_check_when_missing(self, l3acl):
        """create() does not fail on rules without a priority key."""
        rules = [{"description": "no priority"}]
        l3acl.client.post.return_value = {}

        l3acl.create(name="P", l3_rules=rules)  # should not raise

    def test_create_propagates_api_error(self, l3acl, sample_rule):
        """create() lets API errors bubble up."""
        l3acl.client.post.side_effect = RuntimeError("server error")

        with pytest.raises(RuntimeError, match="server error"):
            l3acl.create(name="P", l3_rules=[sample_rule])


# ===================================================================
# update()
# ===================================================================

class TestUpdate:
    """Tests for L3AclPolicies.update()."""

    def test_update_sends_put(self, l3acl, sample_rule):
        """update() PUTs to /l3AclPolicies/{id}."""
        l3acl.client.put.return_value = {"requestId": "r2"}

        result = l3acl.update("pol-1", name="Updated", l3_rules=[sample_rule])

        l3acl.client.put.assert_called_once()
        endpoint = l3acl.client.put.call_args[0][0]
        assert endpoint == "/l3AclPolicies/pol-1"
        assert result == {"requestId": "r2"}

    def test_update_payload_structure(self, l3acl, sample_rule):
        """update() builds the correct payload body."""
        l3acl.client.put.return_value = {}

        l3acl.update(
            "pol-1",
            name="Updated",
            l3_rules=[sample_rule],
            description="new desc",
            default_access="allow",
        )

        data = l3acl.client.put.call_args[1].get("data") or l3acl.client.put.call_args[0][1]
        assert data["name"] == "Updated"
        assert data["l3Rules"] == [sample_rule]
        assert data["description"] == "new desc"
        assert data["defaultAccess"] == "ALLOW"

    def test_update_no_description(self, l3acl, sample_rule):
        """update() omits description when not provided."""
        l3acl.client.put.return_value = {}

        l3acl.update("pol-1", name="Updated", l3_rules=[sample_rule])

        data = l3acl.client.put.call_args[1].get("data") or l3acl.client.put.call_args[0][1]
        assert "description" not in data

    def test_update_kwargs_merged(self, l3acl, sample_rule):
        """update() merges extra kwargs into payload."""
        l3acl.client.put.return_value = {}

        l3acl.update("pol-1", name="P", l3_rules=[sample_rule], venueId="v1")

        data = l3acl.client.put.call_args[1].get("data") or l3acl.client.put.call_args[0][1]
        assert data["venueId"] == "v1"

    def test_update_propagates_exception(self, l3acl, sample_rule):
        """update() lets errors bubble up."""
        l3acl.client.put.side_effect = RuntimeError("timeout")

        with pytest.raises(RuntimeError, match="timeout"):
            l3acl.update("pol-1", name="P", l3_rules=[sample_rule])


# ===================================================================
# delete()
# ===================================================================

class TestDelete:
    """Tests for L3AclPolicies.delete()."""

    def test_delete_calls_correct_endpoint(self, l3acl):
        """delete() sends DELETE to /l3AclPolicies/{id}."""
        l3acl.client.delete.return_value = {"requestId": "r3"}

        result = l3acl.delete("pol-1")

        l3acl.client.delete.assert_called_once_with("/l3AclPolicies/pol-1")
        assert result == {"requestId": "r3"}

    def test_delete_not_found_raises(self, l3acl):
        """delete() raises ResourceNotFoundError with policy ID in message."""
        l3acl.client.delete.side_effect = ResourceNotFoundError()

        with pytest.raises(ResourceNotFoundError, match="pol-1"):
            l3acl.delete("pol-1")

    def test_delete_other_exception_propagates(self, l3acl):
        """delete() does not swallow non-404 exceptions."""
        l3acl.client.delete.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            l3acl.delete("pol-1")


# ===================================================================
# create_rule()  — pure function, no API call
# ===================================================================

class TestCreateRule:
    """Tests for L3AclPolicies.create_rule()."""

    def test_minimal_rule_structure(self, l3acl):
        """create_rule() returns the expected dict with required args only."""
        rule = l3acl.create_rule(description="Block SSH", priority=10)

        assert rule == {
            "description": "Block SSH",
            "priority": 10,
            "access": "ALLOW",
            "source": {"enableIpSubnet": False},
            "destination": {"enableIpSubnet": False},
        }

    def test_access_uppercased(self, l3acl):
        """create_rule() normalises access to uppercase."""
        rule = l3acl.create_rule(description="r", priority=1, access="block")
        assert rule["access"] == "BLOCK"

    def test_no_api_call(self, l3acl):
        """create_rule() is a pure helper; it must not touch the client."""
        l3acl.create_rule(description="r", priority=1)

        l3acl.client.get.assert_not_called()
        l3acl.client.post.assert_not_called()
        l3acl.client.put.assert_not_called()
        l3acl.client.delete.assert_not_called()

    # --- source subnet ---

    def test_source_subnet_enabled(self, l3acl):
        """create_rule() populates source IP fields when subnet is enabled."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            source_enable_ip_subnet=True,
            source_ip="10.0.0.0",
            source_ip_mask="255.255.0.0",
        )

        assert rule["source"] == {
            "enableIpSubnet": True,
            "ip": "10.0.0.0",
            "ipMask": "255.255.0.0",
        }

    def test_source_subnet_enabled_no_mask(self, l3acl):
        """create_rule() omits ipMask when not provided."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            source_enable_ip_subnet=True,
            source_ip="10.0.0.1",
        )

        assert rule["source"] == {
            "enableIpSubnet": True,
            "ip": "10.0.0.1",
        }

    def test_source_ip_ignored_when_subnet_disabled(self, l3acl):
        """create_rule() ignores source_ip when source_enable_ip_subnet is False."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            source_enable_ip_subnet=False,
            source_ip="10.0.0.1",
            source_ip_mask="255.255.255.0",
        )

        assert rule["source"] == {"enableIpSubnet": False}

    # --- destination subnet ---

    def test_destination_subnet_enabled(self, l3acl):
        """create_rule() populates destination IP fields when subnet is enabled."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            destination_enable_ip_subnet=True,
            destination_ip="192.168.1.0",
            destination_ip_mask="255.255.255.0",
        )

        assert rule["destination"] == {
            "enableIpSubnet": True,
            "ip": "192.168.1.0",
            "ipMask": "255.255.255.0",
        }

    def test_destination_subnet_enabled_no_mask(self, l3acl):
        """create_rule() omits ipMask for destination when not provided."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            destination_enable_ip_subnet=True,
            destination_ip="192.168.1.0",
        )

        assert rule["destination"] == {
            "enableIpSubnet": True,
            "ip": "192.168.1.0",
        }

    def test_destination_ip_ignored_when_subnet_disabled(self, l3acl):
        """create_rule() ignores destination_ip when subnet is disabled."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            destination_enable_ip_subnet=False,
            destination_ip="192.168.1.0",
        )

        assert rule["destination"] == {"enableIpSubnet": False}

    # --- destination port ---

    def test_destination_port_included(self, l3acl):
        """create_rule() adds destination port when provided."""
        rule = l3acl.create_rule(description="r", priority=1, destination_port="443")

        assert rule["destination"]["port"] == "443"

    def test_destination_port_absent_by_default(self, l3acl):
        """create_rule() omits destination port when not provided."""
        rule = l3acl.create_rule(description="r", priority=1)

        assert "port" not in rule["destination"]

    # --- kwargs ---

    def test_kwargs_merged_into_rule(self, l3acl):
        """create_rule() merges extra kwargs into the rule dict."""
        rule = l3acl.create_rule(
            description="r",
            priority=1,
            protocol="TCP",
            customField="abc",
        )

        assert rule["protocol"] == "TCP"
        assert rule["customField"] == "abc"

    # --- full combination ---

    def test_full_rule(self, l3acl):
        """create_rule() with all parameters produces the full expected dict."""
        rule = l3acl.create_rule(
            description="Allow HTTPS from LAN",
            priority=5,
            access="ALLOW",
            source_enable_ip_subnet=True,
            source_ip="10.0.0.0",
            source_ip_mask="255.0.0.0",
            destination_enable_ip_subnet=True,
            destination_ip="0.0.0.0",
            destination_ip_mask="0.0.0.0",
            destination_port="443",
        )

        assert rule == {
            "description": "Allow HTTPS from LAN",
            "priority": 5,
            "access": "ALLOW",
            "source": {
                "enableIpSubnet": True,
                "ip": "10.0.0.0",
                "ipMask": "255.0.0.0",
            },
            "destination": {
                "enableIpSubnet": True,
                "ip": "0.0.0.0",
                "ipMask": "0.0.0.0",
                "port": "443",
            },
        }


# ===================================================================
# Module-level constant
# ===================================================================

class TestConstants:
    """Verify public constants are exported correctly."""

    def test_max_rules_is_128(self):
        assert MAX_L3ACL_RULES == 128
