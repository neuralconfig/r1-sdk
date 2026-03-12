"""Comprehensive unit tests for the Identities module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.exceptions import ResourceNotFoundError, ValidationError
from r1_sdk.modules.identities import Identities


@pytest.fixture
def identities():
    client = MagicMock()
    return Identities(client)


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------

class TestList:
    def test_list_default_params(self, identities):
        identities.client.get.return_value = {"data": [], "totalCount": 0}
        result = identities.list()
        identities.client.get.assert_called_once_with(
            "/identities", params={"page": 0, "size": 20}
        )
        assert result == {"data": [], "totalCount": 0}

    def test_list_custom_page_and_size(self, identities):
        identities.client.get.return_value = {"data": []}
        identities.list(page=3, page_size=50)
        identities.client.get.assert_called_once_with(
            "/identities", params={"page": 3, "size": 50}
        )

    def test_list_extra_kwargs(self, identities):
        identities.client.get.return_value = {"data": []}
        identities.list(page=1, page_size=10, groupId="g1", search="alice")
        identities.client.get.assert_called_once_with(
            "/identities",
            params={"page": 1, "size": 10, "groupId": "g1", "search": "alice"},
        )

    def test_list_propagates_exception(self, identities):
        identities.client.get.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            identities.list()


# ---------------------------------------------------------------------------
# query()
# ---------------------------------------------------------------------------

class TestQuery:
    def test_query_default_params(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query()
        identities.client.post.assert_called_once_with(
            "/identities/query", data={"page": 0, "size": 20}
        )

    def test_query_with_dpsk_pool_id(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query(dpsk_pool_id="pool-123")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["dpskPoolId"] == "pool-123"

    def test_query_with_ethernet_port(self, identities):
        identities.client.post.return_value = {"data": []}
        port = {"switch": "sw1", "port": "ge1"}
        identities.query(ethernet_port=port)
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["ethernetPort"] == port

    def test_query_with_filter_params(self, identities):
        identities.client.post.return_value = {"data": []}
        fp = {"name": "alice"}
        identities.query(filter_params=fp)
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["filter"] == fp

    def test_query_with_sort(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query(sort=["name,asc"])
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["sort"] == ["name,asc"]

    def test_query_with_custom_page(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query(page=2, page_size=50)
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["page"] == 2
        assert call_data["size"] == 50

    def test_query_extra_kwargs_merged(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query(customField="value")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["customField"] == "value"

    def test_query_all_params_combined(self, identities):
        identities.client.post.return_value = {"data": []}
        identities.query(
            dpsk_pool_id="pool-1",
            ethernet_port={"port": "ge2"},
            filter_params={"status": "active"},
            page=1,
            page_size=25,
            sort=["name,desc"],
            extra="yes",
        )
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data == {
            "page": 1,
            "size": 25,
            "dpskPoolId": "pool-1",
            "ethernetPort": {"port": "ge2"},
            "filter": {"status": "active"},
            "sort": ["name,desc"],
            "extra": "yes",
        }

    def test_query_propagates_exception(self, identities):
        identities.client.post.side_effect = RuntimeError("fail")
        with pytest.raises(RuntimeError, match="fail"):
            identities.query()

    def test_query_omits_none_optional_fields(self, identities):
        """None optional fields should not appear in the payload."""
        identities.client.post.return_value = {"data": []}
        identities.query()
        call_data = identities.client.post.call_args[1]["data"]
        assert "dpskPoolId" not in call_data
        assert "ethernetPort" not in call_data
        assert "filter" not in call_data
        assert "sort" not in call_data


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestCreate:
    def test_create_minimal(self, identities):
        identities.client.post.return_value = {"id": "i1", "name": "Alice"}
        result = identities.create(group_id="g1", name="Alice")
        identities.client.post.assert_called_once_with(
            "/identityGroups/g1/identities", data={"name": "Alice"}
        )
        assert result["id"] == "i1"

    def test_create_with_all_optional_fields(self, identities):
        identities.client.post.return_value = {"id": "i2"}
        devices = [{"macAddress": "AA-BB-CC-DD-EE-FF"}]
        identities.create(
            group_id="g1",
            name="Bob",
            email="bob@example.com",
            description="Test user",
            expiration_date="2026-12-31T23:59:59Z",
            vlan=100,
            devices=devices,
        )
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["name"] == "Bob"
        assert call_data["email"] == "bob@example.com"
        assert call_data["description"] == "Test user"
        assert call_data["expirationDate"] == "2026-12-31T23:59:59Z"
        assert call_data["vlan"] == 100
        assert call_data["devices"] == devices

    def test_create_with_extra_kwargs(self, identities):
        identities.client.post.return_value = {"id": "i3"}
        identities.create(group_id="g1", name="Carol", customProp="val")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["customProp"] == "val"

    def test_create_vlan_lower_bound(self, identities):
        identities.client.post.return_value = {"id": "i4"}
        identities.create(group_id="g1", name="VlanMin", vlan=1)
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["vlan"] == 1

    def test_create_vlan_upper_bound(self, identities):
        identities.client.post.return_value = {"id": "i5"}
        identities.create(group_id="g1", name="VlanMax", vlan=4094)
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data["vlan"] == 4094

    def test_create_vlan_below_range_raises(self, identities):
        with pytest.raises(ValidationError) as exc_info:
            identities.create(group_id="g1", name="Bad", vlan=0)
        assert exc_info.value.detail == "VLAN must be between 1 and 4094"

    def test_create_vlan_above_range_raises(self, identities):
        with pytest.raises(ValidationError) as exc_info:
            identities.create(group_id="g1", name="Bad", vlan=4095)
        assert exc_info.value.detail == "VLAN must be between 1 and 4094"

    def test_create_vlan_negative_raises(self, identities):
        with pytest.raises(ValidationError) as exc_info:
            identities.create(group_id="g1", name="Bad", vlan=-1)
        assert exc_info.value.detail == "VLAN must be between 1 and 4094"

    def test_create_group_not_found(self, identities):
        identities.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity group with ID g1 not found"):
            identities.create(group_id="g1", name="Alice")

    def test_create_none_optionals_omitted(self, identities):
        """When optional fields are None they should not appear in payload."""
        identities.client.post.return_value = {"id": "i6"}
        identities.create(group_id="g1", name="Sparse")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data == {"name": "Sparse"}


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_get_success(self, identities):
        identities.client.get.return_value = {"id": "i1", "name": "Alice"}
        result = identities.get("g1", "i1")
        identities.client.get.assert_called_once_with(
            "/identityGroups/g1/identities/i1"
        )
        assert result["name"] == "Alice"

    def test_get_not_found(self, identities):
        identities.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.get("g1", "i1")


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_update_sends_patch(self, identities):
        identities.client.patch.return_value = {"id": "i1", "name": "Updated"}
        result = identities.update("g1", "i1", name="Updated", vlan=200)
        identities.client.patch.assert_called_once_with(
            "/identityGroups/g1/identities/i1",
            data={"name": "Updated", "vlan": 200},
        )
        assert result["name"] == "Updated"

    def test_update_no_kwargs_sends_empty(self, identities):
        identities.client.patch.return_value = {}
        identities.update("g1", "i1")
        identities.client.patch.assert_called_once_with(
            "/identityGroups/g1/identities/i1", data={}
        )

    def test_update_not_found(self, identities):
        identities.client.patch.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.update("g1", "i1", name="Nope")


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_success(self, identities):
        identities.client.delete.return_value = None
        identities.delete("g1", "i1")
        identities.client.delete.assert_called_once_with(
            "/identityGroups/g1/identities/i1"
        )

    def test_delete_not_found(self, identities):
        identities.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.delete("g1", "i1")


# ---------------------------------------------------------------------------
# get_devices()
# ---------------------------------------------------------------------------

class TestGetDevices:
    def test_get_devices_returns_list(self, identities):
        devices = [{"macAddress": "AA-BB-CC-DD-EE-FF"}]
        identities.client.get.return_value = {"id": "i1", "devices": devices}
        result = identities.get_devices("g1", "i1")
        assert result == devices

    def test_get_devices_empty_when_missing(self, identities):
        identities.client.get.return_value = {"id": "i1"}
        result = identities.get_devices("g1", "i1")
        assert result == []

    def test_get_devices_not_found(self, identities):
        identities.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.get_devices("g1", "i1")

    def test_get_devices_calls_get_path(self, identities):
        identities.client.get.return_value = {"id": "i1", "devices": []}
        identities.get_devices("g1", "i1")
        identities.client.get.assert_called_once_with(
            "/identityGroups/g1/identities/i1"
        )


# ---------------------------------------------------------------------------
# add_device()
# ---------------------------------------------------------------------------

class TestAddDevice:
    def test_add_device_minimal(self, identities):
        identities.client.post.return_value = {"status": "ok"}
        result = identities.add_device("g1", "i1", "AA-BB-CC-DD-EE-FF")
        identities.client.post.assert_called_once_with(
            "/identityGroups/g1/identities/i1/devices",
            data=[{"macAddress": "AA-BB-CC-DD-EE-FF"}],
        )
        assert result["status"] == "ok"

    def test_add_device_with_name_and_description(self, identities):
        identities.client.post.return_value = {}
        identities.add_device(
            "g1", "i1", "11-22-33-44-55-66",
            name="Laptop", description="Work laptop"
        )
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data == [
            {
                "macAddress": "11-22-33-44-55-66",
                "name": "Laptop",
                "description": "Work laptop",
            }
        ]

    def test_add_device_extra_kwargs(self, identities):
        identities.client.post.return_value = {}
        identities.add_device("g1", "i1", "AA-BB-CC-DD-EE-FF", customField="x")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data[0]["customField"] == "x"

    def test_add_device_lowercase_mac_normalised(self, identities):
        identities.client.post.return_value = {}
        identities.add_device("g1", "i1", "aa-bb-cc-dd-ee-ff")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data[0]["macAddress"] == "AA-BB-CC-DD-EE-FF"

    def test_add_device_mixed_case_mac(self, identities):
        identities.client.post.return_value = {}
        identities.add_device("g1", "i1", "aA-bB-cC-dD-eE-fF")
        call_data = identities.client.post.call_args[1]["data"]
        assert call_data[0]["macAddress"] == "AA-BB-CC-DD-EE-FF"

    def test_add_device_invalid_mac_colon_separator(self, identities):
        with pytest.raises(ValidationError) as exc_info:
            identities.add_device("g1", "i1", "AA:BB:CC:DD:EE:FF")
        assert exc_info.value.detail == "MAC address must be in format XX-XX-XX-XX-XX-XX"

    def test_add_device_invalid_mac_no_separator(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "AABBCCDDEEFF")

    def test_add_device_invalid_mac_too_short(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "AA-BB-CC-DD-EE")

    def test_add_device_invalid_mac_too_long(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "AA-BB-CC-DD-EE-FF-00")

    def test_add_device_invalid_mac_non_hex(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "GG-HH-II-JJ-KK-LL")

    def test_add_device_invalid_mac_empty(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "")

    def test_add_device_invalid_mac_dot_separator(self, identities):
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "AABB.CCDD.EEFF")

    def test_add_device_not_found(self, identities):
        identities.client.post.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.add_device("g1", "i1", "AA-BB-CC-DD-EE-FF")


# ---------------------------------------------------------------------------
# remove_device()
# ---------------------------------------------------------------------------

class TestRemoveDevice:
    def test_remove_device_success(self, identities):
        identities.client.delete.return_value = None
        identities.remove_device("g1", "i1", "AA-BB-CC-DD-EE-FF")
        identities.client.delete.assert_called_once_with(
            "/identityGroups/g1/identities/i1/devices/AA-BB-CC-DD-EE-FF"
        )

    def test_remove_device_not_found(self, identities):
        identities.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="device AA-BB-CC-DD-EE-FF not found"):
            identities.remove_device("g1", "i1", "AA-BB-CC-DD-EE-FF")


# ---------------------------------------------------------------------------
# export_csv()
# ---------------------------------------------------------------------------

class TestExportCsv:
    def test_export_csv_minimal(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"name,email\nAlice,a@b.com\n"
        identities.client.post.return_value = mock_response
        result = identities.export_csv()
        identities.client.post.assert_called_once_with(
            "/identities/csvFile", data={}, raw_response=True
        )
        assert result == b"name,email\nAlice,a@b.com\n"

    def test_export_csv_with_dpsk_pool_id(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"csv"
        identities.client.post.return_value = mock_response
        identities.export_csv(dpsk_pool_id="pool-1")
        call_kwargs = identities.client.post.call_args[1]
        assert call_kwargs["data"]["dpskPoolId"] == "pool-1"

    def test_export_csv_with_filter_params(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"csv"
        identities.client.post.return_value = mock_response
        fp = {"status": "active"}
        identities.export_csv(filter_params=fp)
        call_kwargs = identities.client.post.call_args[1]
        assert call_kwargs["data"]["filter"] == fp

    def test_export_csv_extra_kwargs(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"csv"
        identities.client.post.return_value = mock_response
        identities.export_csv(extra="yes")
        call_kwargs = identities.client.post.call_args[1]
        assert call_kwargs["data"]["extra"] == "yes"

    def test_export_csv_returns_bytes(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"\xef\xbb\xbfname\n"
        identities.client.post.return_value = mock_response
        result = identities.export_csv()
        assert isinstance(result, bytes)

    def test_export_csv_omits_none_fields(self, identities):
        mock_response = MagicMock()
        mock_response.content = b""
        identities.client.post.return_value = mock_response
        identities.export_csv()
        call_kwargs = identities.client.post.call_args[1]
        assert "dpskPoolId" not in call_kwargs["data"]
        assert "filter" not in call_kwargs["data"]

    def test_export_csv_uses_raw_response_flag(self, identities):
        mock_response = MagicMock()
        mock_response.content = b"data"
        identities.client.post.return_value = mock_response
        identities.export_csv()
        call_kwargs = identities.client.post.call_args[1]
        assert call_kwargs["raw_response"] is True


# ---------------------------------------------------------------------------
# import_csv()
# ---------------------------------------------------------------------------

class TestImportCsv:
    def test_import_csv_success(self, identities):
        identities.client.request.return_value = {"imported": 5, "failed": 0}
        csv_data = b"name,email\nAlice,alice@test.com\n"
        result = identities.import_csv("g1", csv_data)
        identities.client.request.assert_called_once()
        call_args = identities.client.request.call_args
        assert call_args[0][0] == 'POST'
        assert call_args[0][1] == "/identityGroups/g1/identities/csvFile"
        assert call_args[1]["files"]["file"][0] == "identities.csv"
        assert call_args[1]["files"]["file"][1] == csv_data
        assert call_args[1]["files"]["file"][2] == "text/csv"
        assert result["imported"] == 5

    def test_import_csv_group_not_found(self, identities):
        identities.client.request.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity group with ID g1 not found"):
            identities.import_csv("g1", b"csv")

    def test_import_csv_file_tuple_structure(self, identities):
        """Verify the files dict has the correct multipart tuple format."""
        identities.client.request.return_value = {}
        csv_data = b"col1,col2\nval1,val2\n"
        identities.import_csv("g1", csv_data)
        call_kwargs = identities.client.request.call_args[1]
        file_tuple = call_kwargs["files"]["file"]
        assert len(file_tuple) == 3
        assert file_tuple[0] == "identities.csv"   # filename
        assert file_tuple[1] is csv_data            # content
        assert file_tuple[2] == "text/csv"          # MIME type


# ---------------------------------------------------------------------------
# Edge cases and cross-method behaviour
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_identities_stores_client_reference(self, identities):
        assert identities.client is not None

    def test_create_vlan_zero_rejected(self, identities):
        with pytest.raises(ValidationError):
            identities.create(group_id="g1", name="Bad", vlan=0)

    def test_create_vlan_none_omitted(self, identities):
        """vlan=None should not add vlan to payload at all."""
        identities.client.post.return_value = {"id": "x"}
        identities.create(group_id="g1", name="Test", vlan=None)
        call_data = identities.client.post.call_args[1]["data"]
        assert "vlan" not in call_data

    def test_add_device_mac_validation_before_api_call(self, identities):
        """MAC validation should happen before any API call is made."""
        with pytest.raises(ValidationError):
            identities.add_device("g1", "i1", "INVALID")
        identities.client.post.assert_not_called()

    def test_create_vlan_validation_before_api_call(self, identities):
        """VLAN validation should happen before any API call is made."""
        with pytest.raises(ValidationError):
            identities.create(group_id="g1", name="Bad", vlan=9999)
        identities.client.post.assert_not_called()

    def test_get_devices_delegates_to_get(self, identities):
        """get_devices should call get() internally, using the same endpoint."""
        identities.client.get.return_value = {
            "id": "i1",
            "devices": [{"macAddress": "00-11-22-33-44-55"}],
        }
        result = identities.get_devices("g1", "i1")
        identities.client.get.assert_called_once_with(
            "/identityGroups/g1/identities/i1"
        )
        assert len(result) == 1

    def test_delete_returns_none(self, identities):
        identities.client.delete.return_value = None
        result = identities.delete("g1", "i1")
        assert result is None

    def test_remove_device_returns_none(self, identities):
        identities.client.delete.return_value = None
        result = identities.remove_device("g1", "i1", "AA-BB-CC-DD-EE-FF")
        assert result is None

    def test_validation_error_has_correct_status_code(self, identities):
        """ValidationError should carry status_code 400."""
        with pytest.raises(ValidationError) as exc_info:
            identities.create(group_id="g1", name="Bad", vlan=0)
        assert exc_info.value.status_code == 400

    def test_resource_not_found_error_has_correct_status_code(self, identities):
        """ResourceNotFoundError should carry status_code 404."""
        identities.client.get.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError) as exc_info:
            identities.get("g1", "i1")
        assert exc_info.value.status_code == 404


# ── list_all ─────────────────────────────────────────────────────────────


class TestListAll:
    """Tests for Identities.list_all()."""

    def test_fetches_all_identities_via_get(self, identities):
        identities.client.get.return_value = {
            "content": [{"id": "id1"}],
            "totalElements": 1,
        }
        result = identities.list_all("g1")
        identities.client.get.assert_called_once_with(
            "/identityGroups/g1/identities",
            params={"page": 0, "size": 100},
        )
        assert result == [{"id": "id1"}]

    def test_paginates_multiple_pages(self, identities):
        identities.client.get.side_effect = [
            {"content": [{"id": "id1"}], "totalElements": 2},
            {"content": [{"id": "id2"}], "totalElements": 2},
        ]
        result = identities.list_all("g1", page_size=1)
        assert result == [{"id": "id1"}, {"id": "id2"}]
        assert identities.client.get.call_count == 2

    def test_passes_kwargs_as_params(self, identities):
        identities.client.get.return_value = {
            "content": [],
            "totalElements": 0,
        }
        identities.list_all("g1", dpskPoolId="pool-1")
        call_params = identities.client.get.call_args[1]["params"]
        assert call_params["dpskPoolId"] == "pool-1"


# ---------------------------------------------------------------------------
# bulk_delete()
# ---------------------------------------------------------------------------

class TestBulkDelete:
    def test_sends_delete_with_id_list(self, identities):
        ids = ["id-1", "id-2", "id-3"]
        identities.bulk_delete("g1", ids)
        identities.client.request.assert_called_once_with(
            'DELETE',
            "/identityGroups/g1/identities",
            json_data=ids,
        )

    def test_returns_none(self, identities):
        result = identities.bulk_delete("g1", ["id-1"])
        assert result is None

    def test_group_not_found(self, identities):
        identities.client.request.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity group with ID g1 not found"):
            identities.bulk_delete("g1", ["id-1"])


# ---------------------------------------------------------------------------
# update_ethernet_ports()
# ---------------------------------------------------------------------------

class TestUpdateEthernetPorts:
    def test_puts_ethernet_ports(self, identities):
        ports = [{"macAddress": "AA-BB-CC-DD-EE-FF", "portIndex": 1}]
        identities.client.put.return_value = {"status": "ok"}
        result = identities.update_ethernet_ports("g1", "i1", "v1", ports)
        identities.client.put.assert_called_once_with(
            "/identityGroups/g1/identities/i1/venues/v1/ethernetPorts",
            data=ports,
        )
        assert result["status"] == "ok"

    def test_not_found(self, identities):
        identities.client.put.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="venue v1 not found"):
            identities.update_ethernet_ports("g1", "i1", "v1", [])


# ---------------------------------------------------------------------------
# delete_ethernet_port()
# ---------------------------------------------------------------------------

class TestDeleteEthernetPort:
    def test_deletes_correct_path(self, identities):
        identities.delete_ethernet_port("g1", "i1", "AA-BB-CC-DD-EE-FF", 3)
        identities.client.delete.assert_called_once_with(
            "/identityGroups/g1/identities/i1/ethernetPorts/AA-BB-CC-DD-EE-FF/3"
        )

    def test_returns_none(self, identities):
        identities.client.delete.return_value = None
        result = identities.delete_ethernet_port("g1", "i1", "AA-BB-CC-DD-EE-FF", 1)
        assert result is None

    def test_not_found(self, identities):
        identities.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Ethernet port AA-BB-CC-DD-EE-FF/3"):
            identities.delete_ethernet_port("g1", "i1", "AA-BB-CC-DD-EE-FF", 3)


# ---------------------------------------------------------------------------
# retry_vni_allocation()
# ---------------------------------------------------------------------------

class TestRetryVniAllocation:
    def test_deletes_vnis_path(self, identities):
        identities.retry_vni_allocation("g1", "i1")
        identities.client.delete.assert_called_once_with(
            "/identityGroups/g1/identities/i1/vnis"
        )

    def test_returns_none(self, identities):
        identities.client.delete.return_value = None
        result = identities.retry_vni_allocation("g1", "i1")
        assert result is None

    def test_not_found(self, identities):
        identities.client.delete.side_effect = ResourceNotFoundError()
        with pytest.raises(ResourceNotFoundError, match="Identity i1 in group g1 not found"):
            identities.retry_vni_allocation("g1", "i1")
