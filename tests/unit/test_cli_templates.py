"""Comprehensive unit tests for the CLITemplates module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.exceptions import ResourceNotFoundError
from r1_sdk.modules.cli_templates import CLITemplates


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a mock R1Client."""
    return MagicMock()


@pytest.fixture
def cli_templates(client):
    """Create a CLITemplates instance backed by a mock client."""
    return CLITemplates(client)


# Sample data helpers
TEMPLATE_ID = "tmpl-001"
VENUE_ID = "venue-001"


def _make_template(
    template_id=TEMPLATE_ID,
    name="my-template",
    cli="show version",
    variables=None,
    venue_switches=None,
):
    """Return a realistic template dict."""
    t = {
        "id": template_id,
        "name": name,
        "cli": cli,
        "reload": False,
        "variables": variables or [],
        "venueSwitches": venue_switches or [],
    }
    return t


# ===================================================================
# list()
# ===================================================================

class TestList:
    def test_returns_list_from_api(self, cli_templates, client):
        templates = [_make_template(), _make_template("tmpl-002", "other")]
        client.get.return_value = templates

        result = cli_templates.list()

        client.get.assert_called_once_with("/cliTemplates")
        assert result == templates

    def test_returns_empty_list_when_api_returns_non_list(self, cli_templates, client):
        client.get.return_value = {"unexpected": "dict"}

        result = cli_templates.list()

        assert result == []

    def test_returns_empty_list_when_api_returns_none(self, cli_templates, client):
        client.get.return_value = None

        result = cli_templates.list()

        assert result == []

    def test_returns_empty_list_when_api_returns_string(self, cli_templates, client):
        client.get.return_value = "not a list"

        result = cli_templates.list()

        assert result == []

    def test_propagates_exception(self, cli_templates, client):
        client.get.side_effect = RuntimeError("connection error")

        with pytest.raises(RuntimeError, match="connection error"):
            cli_templates.list()


# ===================================================================
# get()
# ===================================================================

class TestGet:
    def test_returns_template(self, cli_templates, client):
        template = _make_template()
        client.get.return_value = template

        result = cli_templates.get(TEMPLATE_ID)

        client.get.assert_called_once_with(f"/cliTemplates/{TEMPLATE_ID}")
        assert result == template

    def test_raises_resource_not_found(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.get(TEMPLATE_ID)

    def test_not_found_message_contains_id(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match=TEMPLATE_ID):
            cli_templates.get(TEMPLATE_ID)


# ===================================================================
# create()
# ===================================================================

class TestCreate:
    def test_minimal_create(self, cli_templates, client):
        client.post.return_value = _make_template()

        result = cli_templates.create(name="my-template", cli="show version")

        client.post.assert_called_once_with(
            "/cliTemplates",
            data={
                "name": "my-template",
                "cli": "show version",
                "reload": False,
            },
        )
        assert result["name"] == "my-template"

    def test_create_with_reload(self, cli_templates, client):
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd", reload=True)

        posted_data = client.post.call_args[1]["data"]
        assert posted_data["reload"] is True

    def test_create_with_variables(self, cli_templates, client):
        variables = [{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        client.post.return_value = _make_template(variables=variables)

        cli_templates.create(name="t", cli="cmd", variables=variables)

        posted_data = client.post.call_args[1]["data"]
        assert posted_data["variables"] == variables

    def test_create_with_venue_switches(self, cli_templates, client):
        vs = [{"venueId": VENUE_ID, "switches": ["sw1"]}]
        client.post.return_value = _make_template(venue_switches=vs)

        cli_templates.create(name="t", cli="cmd", venue_switches=vs)

        posted_data = client.post.call_args[1]["data"]
        assert posted_data["venueSwitches"] == vs

    def test_create_with_kwargs(self, cli_templates, client):
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd", description="extra field")

        posted_data = client.post.call_args[1]["data"]
        assert posted_data["description"] == "extra field"

    def test_variables_not_in_payload_when_none(self, cli_templates, client):
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd")

        posted_data = client.post.call_args[1]["data"]
        assert "variables" not in posted_data

    def test_venue_switches_not_in_payload_when_none(self, cli_templates, client):
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd")

        posted_data = client.post.call_args[1]["data"]
        assert "venueSwitches" not in posted_data

    def test_propagates_exception(self, cli_templates, client):
        client.post.side_effect = RuntimeError("server error")

        with pytest.raises(RuntimeError, match="server error"):
            cli_templates.create(name="t", cli="cmd")


# ===================================================================
# update()
# ===================================================================

class TestUpdate:
    def test_update_with_kwargs(self, cli_templates, client):
        updated = _make_template(name="new-name")
        client.put.return_value = updated

        result = cli_templates.update(TEMPLATE_ID, name="new-name")

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"name": "new-name"},
        )
        assert result["name"] == "new-name"

    def test_raises_resource_not_found(self, cli_templates, client):
        client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match=TEMPLATE_ID):
            cli_templates.update(TEMPLATE_ID, name="x")


# ===================================================================
# delete()
# ===================================================================

class TestDelete:
    def test_delete_calls_client(self, cli_templates, client):
        cli_templates.delete(TEMPLATE_ID)

        client.delete.assert_called_once_with(f"/cliTemplates/{TEMPLATE_ID}")

    def test_delete_returns_none(self, cli_templates, client):
        result = cli_templates.delete(TEMPLATE_ID)

        assert result is None

    def test_raises_resource_not_found(self, cli_templates, client):
        client.delete.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match=TEMPLATE_ID):
            cli_templates.delete(TEMPLATE_ID)


# ===================================================================
# query()
# ===================================================================

class TestQuery:
    def test_default_query(self, cli_templates, client):
        client.post.return_value = {"data": [], "total": 0}

        cli_templates.query()

        client.post.assert_called_once_with(
            "/cliTemplates/query",
            data={"pageSize": 100, "page": 1, "sortOrder": "ASC"},
        )

    def test_custom_query(self, cli_templates, client):
        query = {"pageSize": 10, "page": 2, "sortOrder": "DESC"}
        client.post.return_value = {"data": [], "total": 0}

        cli_templates.query(query_data=query)

        client.post.assert_called_once_with("/cliTemplates/query", data=query)

    def test_sort_order_uppercased(self, cli_templates, client):
        query = {"sortOrder": "desc"}
        client.post.return_value = {"data": []}

        cli_templates.query(query_data=query)

        passed_data = client.post.call_args[1]["data"]
        assert passed_data["sortOrder"] == "DESC"

    def test_query_with_filters(self, cli_templates, client):
        query = {
            "filters": [{"type": "NAME", "value": "test"}],
            "pageSize": 50,
            "page": 1,
            "sortOrder": "ASC",
        }
        client.post.return_value = {"data": [_make_template()], "total": 1}

        result = cli_templates.query(query_data=query)

        assert result["total"] == 1

    def test_propagates_exception(self, cli_templates, client):
        client.post.side_effect = RuntimeError("api error")

        with pytest.raises(RuntimeError):
            cli_templates.query()


# ===================================================================
# get_examples()
# ===================================================================

class TestGetExamples:
    def test_returns_list(self, cli_templates, client):
        examples = [{"name": "VLAN config", "cli": "vlan 100"}]
        client.get.return_value = examples

        result = cli_templates.get_examples()

        client.get.assert_called_once_with("/cliTemplates/examples")
        assert result == examples

    def test_returns_empty_when_non_list(self, cli_templates, client):
        client.get.return_value = {"not": "a list"}

        result = cli_templates.get_examples()

        assert result == []

    def test_propagates_exception(self, cli_templates, client):
        client.get.side_effect = RuntimeError("fail")

        with pytest.raises(RuntimeError):
            cli_templates.get_examples()


# ===================================================================
# bulk_delete()
# ===================================================================

class TestBulkDelete:
    def test_sends_ids_via_request(self, cli_templates, client):
        ids = ["id-1", "id-2", "id-3"]
        client.request.return_value = {"deleted": 3}

        result = cli_templates.bulk_delete(ids)

        client.request.assert_called_once_with(
            "DELETE", "/cliTemplates", json_data=ids
        )
        assert result["deleted"] == 3

    def test_propagates_exception(self, cli_templates, client):
        client.request.side_effect = RuntimeError("fail")

        with pytest.raises(RuntimeError):
            cli_templates.bulk_delete(["id-1"])


# ===================================================================
# associate_with_venue() / disassociate_from_venue()
# ===================================================================

class TestVenueAssociation:
    def test_associate_calls_put(self, cli_templates, client):
        client.put.return_value = {"status": "ok"}

        result = cli_templates.associate_with_venue(VENUE_ID, TEMPLATE_ID)

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/cliTemplates/{TEMPLATE_ID}",
            data={},
        )
        assert result == {"status": "ok"}

    def test_associate_with_kwargs(self, cli_templates, client):
        client.put.return_value = {"status": "ok"}

        cli_templates.associate_with_venue(
            VENUE_ID, TEMPLATE_ID, priority=1, enabled=True
        )

        client.put.assert_called_once_with(
            f"/venues/{VENUE_ID}/cliTemplates/{TEMPLATE_ID}",
            data={"priority": 1, "enabled": True},
        )

    def test_associate_raises_not_found(self, cli_templates, client):
        client.put.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.associate_with_venue(VENUE_ID, TEMPLATE_ID)

    def test_disassociate_calls_delete(self, cli_templates, client):
        cli_templates.disassociate_from_venue(VENUE_ID, TEMPLATE_ID)

        client.delete.assert_called_once_with(
            f"/venues/{VENUE_ID}/cliTemplates/{TEMPLATE_ID}"
        )

    def test_disassociate_returns_none(self, cli_templates, client):
        result = cli_templates.disassociate_from_venue(VENUE_ID, TEMPLATE_ID)

        assert result is None

    def test_disassociate_raises_not_found(self, cli_templates, client):
        client.delete.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.disassociate_from_venue(VENUE_ID, TEMPLATE_ID)


# ===================================================================
# get_variables()
# ===================================================================

class TestGetVariables:
    def test_returns_variables_list(self, cli_templates, client):
        variables = [
            {"name": "mgmt_ip", "type": "ADDRESS", "value": "10.0.0.1"},
            {"name": "hostname", "type": "STRING", "value": "switch1"},
        ]
        client.get.return_value = _make_template(variables=variables)

        result = cli_templates.get_variables(TEMPLATE_ID)

        assert result == variables
        client.get.assert_called_once_with(f"/cliTemplates/{TEMPLATE_ID}")

    def test_returns_empty_when_no_variables(self, cli_templates, client):
        client.get.return_value = _make_template()

        result = cli_templates.get_variables(TEMPLATE_ID)

        assert result == []

    def test_returns_empty_when_variables_key_missing(self, cli_templates, client):
        template = {"id": TEMPLATE_ID, "name": "t", "cli": "cmd"}
        client.get.return_value = template

        result = cli_templates.get_variables(TEMPLATE_ID)

        assert result == []

    def test_raises_not_found(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError, match=TEMPLATE_ID):
            cli_templates.get_variables(TEMPLATE_ID)


# ===================================================================
# add_variable()
# ===================================================================

class TestAddVariable:
    def test_appends_variable_to_empty_list(self, cli_templates, client):
        client.get.return_value = _make_template(variables=[])
        client.put.return_value = _make_template(
            variables=[{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        )
        new_var = {"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}

        result = cli_templates.add_variable(TEMPLATE_ID, new_var)

        # Verify update was called with the appended variable
        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": [new_var]},
        )
        assert result["variables"] == [new_var]

    def test_appends_variable_to_existing_list(self, cli_templates, client):
        existing = [{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        new_var = {"name": "hostname", "type": "STRING", "value": "sw1"}
        client.get.return_value = _make_template(variables=list(existing))
        client.put.return_value = _make_template(variables=existing + [new_var])

        cli_templates.add_variable(TEMPLATE_ID, new_var)

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": existing + [new_var]},
        )

    def test_raises_value_error_on_duplicate_name(self, cli_templates, client):
        existing = [{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        client.get.return_value = _make_template(variables=existing)

        with pytest.raises(ValueError, match="ip"):
            cli_templates.add_variable(
                TEMPLATE_ID,
                {"name": "ip", "type": "STRING", "value": "different"},
            )

        # update should NOT have been called
        client.put.assert_not_called()

    def test_raises_not_found_when_template_missing(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.add_variable(
                TEMPLATE_ID,
                {"name": "v", "type": "STRING", "value": "x"},
            )


# ===================================================================
# update_variable()
# ===================================================================

class TestUpdateVariable:
    def test_updates_matching_variable(self, cli_templates, client):
        original = [
            {"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"},
            {"name": "hostname", "type": "STRING", "value": "sw1"},
        ]
        updated_var = {"name": "ip", "type": "ADDRESS", "value": "192.168.1.1"}
        client.get.return_value = _make_template(variables=list(original))
        client.put.return_value = _make_template(
            variables=[updated_var, original[1]]
        )

        cli_templates.update_variable(TEMPLATE_ID, "ip", updated_var)

        expected_vars = [updated_var, original[1]]
        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": expected_vars},
        )

    def test_raises_not_found_when_variable_missing(self, cli_templates, client):
        client.get.return_value = _make_template(
            variables=[{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        )

        with pytest.raises(ResourceNotFoundError, match="nonexistent"):
            cli_templates.update_variable(
                TEMPLATE_ID,
                "nonexistent",
                {"name": "nonexistent", "type": "STRING", "value": "x"},
            )

    def test_raises_not_found_when_template_missing(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.update_variable(
                TEMPLATE_ID,
                "ip",
                {"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"},
            )

    def test_replaces_entire_variable_dict(self, cli_templates, client):
        """The updated variable_data fully replaces the matched entry."""
        original = [{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        replacement = {"name": "ip", "type": "STRING", "value": "changed", "extra": True}
        client.get.return_value = _make_template(variables=list(original))
        client.put.return_value = _make_template(variables=[replacement])

        cli_templates.update_variable(TEMPLATE_ID, "ip", replacement)

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": [replacement]},
        )


# ===================================================================
# delete_variable()
# ===================================================================

class TestDeleteVariable:
    def test_removes_matching_variable(self, cli_templates, client):
        variables = [
            {"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"},
            {"name": "hostname", "type": "STRING", "value": "sw1"},
        ]
        client.get.return_value = _make_template(variables=list(variables))
        client.put.return_value = _make_template(variables=[variables[1]])

        cli_templates.delete_variable(TEMPLATE_ID, "ip")

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": [variables[1]]},
        )

    def test_removing_last_variable_leaves_empty_list(self, cli_templates, client):
        variables = [{"name": "ip", "type": "ADDRESS", "value": "10.0.0.1"}]
        client.get.return_value = _make_template(variables=list(variables))
        client.put.return_value = _make_template(variables=[])

        cli_templates.delete_variable(TEMPLATE_ID, "ip")

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={"variables": []},
        )

    def test_raises_not_found_when_variable_missing(self, cli_templates, client):
        client.get.return_value = _make_template(variables=[])

        with pytest.raises(ResourceNotFoundError, match="nonexistent"):
            cli_templates.delete_variable(TEMPLATE_ID, "nonexistent")

    def test_raises_not_found_when_template_missing(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.delete_variable(TEMPLATE_ID, "ip")


# ===================================================================
# get_venue_switches()
# ===================================================================

class TestGetVenueSwitches:
    def test_returns_venue_switches(self, cli_templates, client):
        vs = [{"venueId": VENUE_ID, "switches": ["sw1", "sw2"]}]
        client.get.return_value = _make_template(venue_switches=vs)

        result = cli_templates.get_venue_switches(TEMPLATE_ID)

        assert result == vs

    def test_returns_empty_when_none(self, cli_templates, client):
        client.get.return_value = _make_template()

        result = cli_templates.get_venue_switches(TEMPLATE_ID)

        assert result == []

    def test_returns_empty_when_key_missing(self, cli_templates, client):
        client.get.return_value = {"id": TEMPLATE_ID, "name": "t"}

        result = cli_templates.get_venue_switches(TEMPLATE_ID)

        assert result == []

    def test_raises_not_found(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.get_venue_switches(TEMPLATE_ID)


# ===================================================================
# add_venue_switches()
# ===================================================================

class TestAddVenueSwitches:
    def test_creates_new_venue_mapping(self, cli_templates, client):
        client.get.return_value = _make_template(venue_switches=[])
        client.put.return_value = _make_template(
            venue_switches=[{"venueId": VENUE_ID, "switches": ["sw1", "sw2"]}]
        )

        cli_templates.add_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1", "sw2"])

        client.put.assert_called_once_with(
            f"/cliTemplates/{TEMPLATE_ID}",
            data={
                "venueSwitches": [
                    {"venueId": VENUE_ID, "switches": ["sw1", "sw2"]}
                ]
            },
        )

    def test_appends_to_existing_venue_mapping(self, cli_templates, client):
        existing_vs = [{"venueId": VENUE_ID, "switches": ["sw1"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.add_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw2", "sw3"])

        put_data = client.put.call_args[1]["data"]
        vs = put_data["venueSwitches"]
        assert len(vs) == 1
        assert vs[0]["venueId"] == VENUE_ID
        # sw1 was existing, sw2 and sw3 are new -- all should be present
        assert set(vs[0]["switches"]) == {"sw1", "sw2", "sw3"}

    def test_deduplicates_switch_ids(self, cli_templates, client):
        existing_vs = [{"venueId": VENUE_ID, "switches": ["sw1", "sw2"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.add_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw2", "sw3"])

        put_data = client.put.call_args[1]["data"]
        switches = put_data["venueSwitches"][0]["switches"]
        # No duplicates -- sw2 was already present
        assert len(switches) == len(set(switches))
        assert set(switches) == {"sw1", "sw2", "sw3"}

    def test_adds_new_venue_alongside_existing(self, cli_templates, client):
        """When a different venue already has switches, a new venue mapping is added."""
        other_venue_id = "venue-other"
        existing_vs = [{"venueId": other_venue_id, "switches": ["sw-a"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.add_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])

        put_data = client.put.call_args[1]["data"]
        vs = put_data["venueSwitches"]
        assert len(vs) == 2
        venue_ids = {v["venueId"] for v in vs}
        assert venue_ids == {other_venue_id, VENUE_ID}

    def test_raises_not_found(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.add_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])


# ===================================================================
# remove_venue_switches()
# ===================================================================

class TestRemoveVenueSwitches:
    def test_removes_specified_switches(self, cli_templates, client):
        existing_vs = [{"venueId": VENUE_ID, "switches": ["sw1", "sw2", "sw3"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.remove_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1", "sw3"])

        put_data = client.put.call_args[1]["data"]
        vs = put_data["venueSwitches"]
        assert len(vs) == 1
        assert vs[0]["switches"] == ["sw2"]

    def test_removes_venue_mapping_when_empty(self, cli_templates, client):
        """If all switches are removed, the entire venue mapping is dropped."""
        existing_vs = [{"venueId": VENUE_ID, "switches": ["sw1"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.remove_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])

        put_data = client.put.call_args[1]["data"]
        assert put_data["venueSwitches"] == []

    def test_only_affects_target_venue(self, cli_templates, client):
        other_venue_id = "venue-other"
        existing_vs = [
            {"venueId": VENUE_ID, "switches": ["sw1", "sw2"]},
            {"venueId": other_venue_id, "switches": ["sw-a"]},
        ]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.remove_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])

        put_data = client.put.call_args[1]["data"]
        vs = put_data["venueSwitches"]
        assert len(vs) == 2
        for mapping in vs:
            if mapping["venueId"] == VENUE_ID:
                assert mapping["switches"] == ["sw2"]
            else:
                assert mapping["switches"] == ["sw-a"]

    def test_noop_when_venue_not_found(self, cli_templates, client):
        """If the venue_id is not in the mapping, nothing changes."""
        existing_vs = [{"venueId": "other-venue", "switches": ["sw1"]}]
        client.get.return_value = _make_template(venue_switches=existing_vs)
        client.put.return_value = MagicMock()

        cli_templates.remove_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])

        put_data = client.put.call_args[1]["data"]
        # Original mapping is unchanged
        assert put_data["venueSwitches"] == existing_vs

    def test_raises_not_found(self, cli_templates, client):
        client.get.side_effect = ResourceNotFoundError(message="not found")

        with pytest.raises(ResourceNotFoundError):
            cli_templates.remove_venue_switches(TEMPLATE_ID, VENUE_ID, ["sw1"])


# ===================================================================
# Edge cases / integration-like tests within unit scope
# ===================================================================

class TestEdgeCases:
    def test_constructor_stores_client(self, client):
        ct = CLITemplates(client)
        assert ct.client is client

    def test_create_empty_variables_list_not_included(self, cli_templates, client):
        """An empty list for variables should not be sent (falsy)."""
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd", variables=[])

        posted_data = client.post.call_args[1]["data"]
        assert "variables" not in posted_data

    def test_create_empty_venue_switches_list_not_included(self, cli_templates, client):
        """An empty list for venue_switches should not be sent (falsy)."""
        client.post.return_value = _make_template()

        cli_templates.create(name="t", cli="cmd", venue_switches=[])

        posted_data = client.post.call_args[1]["data"]
        assert "venueSwitches" not in posted_data

    def test_query_without_sort_order_no_uppercase(self, cli_templates, client):
        """query_data without sortOrder key should not cause KeyError."""
        query = {"pageSize": 10, "page": 1}
        client.post.return_value = {"data": []}

        cli_templates.query(query_data=query)

        passed_data = client.post.call_args[1]["data"]
        assert "sortOrder" not in passed_data

    def test_add_variable_does_not_mutate_template_dict(self, cli_templates, client):
        """add_variable should not accidentally mutate the returned template dict."""
        original_vars = []
        template = _make_template(variables=original_vars)
        client.get.return_value = template
        client.put.return_value = _make_template(
            variables=[{"name": "v", "type": "STRING", "value": "x"}]
        )

        cli_templates.add_variable(
            TEMPLATE_ID, {"name": "v", "type": "STRING", "value": "x"}
        )

        # The variable list in put call should contain the new variable
        put_vars = client.put.call_args[1]["data"]["variables"]
        assert len(put_vars) == 1
