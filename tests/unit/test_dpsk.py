"""Unit tests for the DPSK (Dynamic Pre-Shared Key) module."""

from unittest.mock import MagicMock, call

import pytest

from r1_sdk.modules.dpsk import DPSK


@pytest.fixture
def dpsk():
    client = MagicMock()
    return DPSK(client)


# ---------------------------------------------------------------------------
# Service management
# ---------------------------------------------------------------------------

class TestListServices:
    """Tests for DPSK.list_services()."""

    def test_no_filters(self, dpsk):
        """Should POST empty dict when no filters provided."""
        dpsk.client.post.return_value = {"data": [{"id": "pool-1"}]}
        result = dpsk.list_services()
        dpsk.client.post.assert_called_once_with("/dpskServices/query", {})
        assert result == [{"id": "pool-1"}]

    def test_with_filters(self, dpsk):
        """Should extract recognized filter keys and POST them."""
        filters = {
            "page": 1,
            "pageSize": 50,
            "sortOrder": "asc",
            "sortField": "name",
            "searchString": "guest",
            "searchTargetFields": ["name"],
            "fields": ["id", "name"],
            "filters": [{"field": "status", "value": "active"}],
        }
        dpsk.client.post.return_value = {"data": [{"id": "pool-2"}]}
        result = dpsk.list_services(filters=filters)
        dpsk.client.post.assert_called_once_with("/dpskServices/query", filters)
        assert result == [{"id": "pool-2"}]

    def test_filters_ignores_unknown_keys(self, dpsk):
        """Should not pass unrecognized keys to the API."""
        filters = {"page": 1, "unknownKey": "ignored"}
        dpsk.client.post.return_value = {"data": []}
        dpsk.list_services(filters=filters)
        dpsk.client.post.assert_called_once_with("/dpskServices/query", {"page": 1})

    def test_filters_skips_none_values(self, dpsk):
        """Should skip filter keys whose value is None."""
        filters = {"page": 1, "pageSize": None}
        dpsk.client.post.return_value = {"data": []}
        dpsk.list_services(filters=filters)
        dpsk.client.post.assert_called_once_with("/dpskServices/query", {"page": 1})

    def test_response_dict_returns_data(self, dpsk):
        """Should return the 'data' key from a dict response."""
        dpsk.client.post.return_value = {"data": [{"id": "a"}, {"id": "b"}], "total": 2}
        result = dpsk.list_services()
        assert result == [{"id": "a"}, {"id": "b"}]

    def test_response_dict_missing_data_key(self, dpsk):
        """Should return empty list if dict response lacks 'data' key."""
        dpsk.client.post.return_value = {"total": 0}
        result = dpsk.list_services()
        assert result == []

    def test_response_list(self, dpsk):
        """Should return the list directly if response is a list."""
        dpsk.client.post.return_value = [{"id": "x"}]
        result = dpsk.list_services()
        assert result == [{"id": "x"}]

    def test_response_unexpected_type(self, dpsk):
        """Should return empty list for unexpected response types."""
        dpsk.client.post.return_value = "unexpected"
        result = dpsk.list_services()
        assert result == []

    def test_propagates_exception(self, dpsk):
        """Should re-raise exceptions from the client."""
        dpsk.client.post.side_effect = RuntimeError("connection failed")
        with pytest.raises(RuntimeError, match="connection failed"):
            dpsk.list_services()


class TestGetService:
    """Tests for DPSK.get_service()."""

    def test_gets_by_pool_id(self, dpsk):
        expected = {"id": "pool-1", "name": "Guest DPSK"}
        dpsk.client.get.return_value = expected
        result = dpsk.get_service("pool-1")
        dpsk.client.get.assert_called_once_with("/dpskServices/pool-1")
        assert result == expected


class TestCreateService:
    """Tests for DPSK.create_service()."""

    def test_name_only(self, dpsk):
        dpsk.client.post.return_value = {"id": "new-pool", "name": "TestPool"}
        result = dpsk.create_service("TestPool")
        dpsk.client.post.assert_called_once_with("/dpskServices", {"name": "TestPool"})
        assert result["name"] == "TestPool"

    def test_name_with_kwargs(self, dpsk):
        dpsk.client.post.return_value = {"id": "new-pool"}
        dpsk.create_service("TestPool", vlanId=100, groupDpsk=True)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices",
            {"name": "TestPool", "vlanId": 100, "groupDpsk": True},
        )


class TestUpdateService:
    """Tests for DPSK.update_service()."""

    def test_puts_updates(self, dpsk):
        updates = {"name": "Renamed"}
        dpsk.client.put.return_value = {"id": "pool-1", "name": "Renamed"}
        result = dpsk.update_service("pool-1", updates)
        dpsk.client.put.assert_called_once_with("/dpskServices/pool-1", updates)
        assert result["name"] == "Renamed"


class TestDeleteService:
    """Tests for DPSK.delete_service()."""

    def test_deletes_by_pool_id(self, dpsk):
        dpsk.delete_service("pool-1")
        dpsk.client.delete.assert_called_once_with("/dpskServices/pool-1")

    def test_returns_none(self, dpsk):
        result = dpsk.delete_service("pool-1")
        assert result is None


# ---------------------------------------------------------------------------
# Passphrase management
# ---------------------------------------------------------------------------

class TestListPassphrases:
    """Tests for DPSK.list_passphrases()."""

    def test_no_filters(self, dpsk):
        dpsk.client.post.return_value = {"data": [{"id": "pp-1"}]}
        result = dpsk.list_passphrases("pool-1")
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query", {}
        )
        assert result == [{"id": "pp-1"}]

    def test_with_filters(self, dpsk):
        filters = {"page": 0, "pageSize": 100, "searchString": "user1"}
        dpsk.client.post.return_value = {"data": []}
        dpsk.list_passphrases("pool-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query", filters
        )

    def test_filters_ignores_unknown_keys(self, dpsk):
        filters = {"pageSize": 10, "bogus": "nope"}
        dpsk.client.post.return_value = {"data": []}
        dpsk.list_passphrases("pool-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query", {"pageSize": 10}
        )

    def test_filters_skips_none_values(self, dpsk):
        filters = {"page": 0, "sortOrder": None}
        dpsk.client.post.return_value = {"data": []}
        dpsk.list_passphrases("pool-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query", {"page": 0}
        )

    def test_response_dict(self, dpsk):
        dpsk.client.post.return_value = {"data": [{"id": "pp-1"}], "total": 1}
        assert dpsk.list_passphrases("pool-1") == [{"id": "pp-1"}]

    def test_response_dict_missing_data(self, dpsk):
        dpsk.client.post.return_value = {"total": 0}
        assert dpsk.list_passphrases("pool-1") == []

    def test_response_list(self, dpsk):
        dpsk.client.post.return_value = [{"id": "pp-1"}]
        assert dpsk.list_passphrases("pool-1") == [{"id": "pp-1"}]

    def test_response_unexpected_type(self, dpsk):
        dpsk.client.post.return_value = 42
        assert dpsk.list_passphrases("pool-1") == []

    def test_propagates_exception(self, dpsk):
        dpsk.client.post.side_effect = ValueError("bad request")
        with pytest.raises(ValueError, match="bad request"):
            dpsk.list_passphrases("pool-1")


class TestGetPassphrase:
    """Tests for DPSK.get_passphrase()."""

    def test_gets_by_ids(self, dpsk):
        expected = {"id": "pp-1", "passphrase": "secret123"}
        dpsk.client.get.return_value = expected
        result = dpsk.get_passphrase("pool-1", "pp-1")
        dpsk.client.get.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1"
        )
        assert result == expected


class TestCreatePassphrases:
    """Tests for DPSK.create_passphrases()."""

    def test_single_passphrase(self, dpsk):
        passphrases = [{"passphrase": "abc123", "userName": "user1"}]
        dpsk.client.post.return_value = {"id": "pp-new"}
        result = dpsk.create_passphrases("pool-1", passphrases)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases",
            {"passphrases": passphrases},
        )
        assert result == {"id": "pp-new"}

    def test_multiple_passphrases(self, dpsk):
        passphrases = [
            {"passphrase": "abc", "userName": "u1"},
            {"passphrase": "def", "userName": "u2"},
        ]
        dpsk.client.post.return_value = {"created": 2}
        dpsk.create_passphrases("pool-1", passphrases)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases",
            {"passphrases": passphrases},
        )


class TestUpdatePassphrase:
    """Tests for DPSK.update_passphrase()."""

    def test_puts_updates(self, dpsk):
        updates = {"userName": "new-name"}
        dpsk.client.put.return_value = {"id": "pp-1", "userName": "new-name"}
        result = dpsk.update_passphrase("pool-1", "pp-1", updates)
        dpsk.client.put.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1", updates
        )
        assert result["userName"] == "new-name"


class TestDeletePassphrases:
    """Tests for DPSK.delete_passphrases()."""

    def test_deletes_by_ids(self, dpsk):
        ids = ["pp-1", "pp-2"]
        dpsk.delete_passphrases("pool-1", ids)
        dpsk.client.delete.assert_called_once_with(
            "/dpskServices/pool-1/passphrases",
            json_data={"passphraseIds": ids},
        )

    def test_returns_none(self, dpsk):
        result = dpsk.delete_passphrases("pool-1", ["pp-1"])
        assert result is None


class TestBatchUpdatePassphrases:
    """Tests for DPSK.batch_update_passphrases()."""

    def test_patches_multiple(self, dpsk):
        updates = [
            {"id": "pp-1", "userName": "a"},
            {"id": "pp-2", "userName": "b"},
        ]
        dpsk.client.patch.return_value = {"updated": 2}
        result = dpsk.batch_update_passphrases("pool-1", updates)
        dpsk.client.patch.assert_called_once_with(
            "/dpskServices/pool-1/passphrases",
            {"passphrases": updates},
        )
        assert result == {"updated": 2}


# ---------------------------------------------------------------------------
# Device management
# ---------------------------------------------------------------------------

class TestListDevices:
    """Tests for DPSK.list_devices()."""

    def test_returns_list_response(self, dpsk):
        dpsk.client.get.return_value = [{"mac": "AA:BB:CC:DD:EE:FF"}]
        result = dpsk.list_devices("pool-1", "pp-1")
        dpsk.client.get.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices"
        )
        assert result == [{"mac": "AA:BB:CC:DD:EE:FF"}]

    def test_returns_dict_with_devices_key(self, dpsk):
        dpsk.client.get.return_value = {"devices": [{"mac": "11:22:33:44:55:66"}]}
        result = dpsk.list_devices("pool-1", "pp-1")
        assert result == [{"mac": "11:22:33:44:55:66"}]

    def test_returns_dict_with_data_key(self, dpsk):
        dpsk.client.get.return_value = {"data": [{"mac": "AA:BB:CC:DD:EE:FF"}]}
        result = dpsk.list_devices("pool-1", "pp-1")
        assert result == [{"mac": "AA:BB:CC:DD:EE:FF"}]

    def test_dict_prefers_devices_over_data(self, dpsk):
        """When both 'devices' and 'data' exist, 'devices' takes precedence."""
        dpsk.client.get.return_value = {
            "devices": [{"mac": "AA:AA:AA:AA:AA:AA"}],
            "data": [{"mac": "BB:BB:BB:BB:BB:BB"}],
        }
        result = dpsk.list_devices("pool-1", "pp-1")
        assert result == [{"mac": "AA:AA:AA:AA:AA:AA"}]

    def test_returns_empty_for_unexpected_type(self, dpsk):
        dpsk.client.get.return_value = "unexpected"
        result = dpsk.list_devices("pool-1", "pp-1")
        assert result == []

    def test_returns_empty_for_dict_without_known_keys(self, dpsk):
        dpsk.client.get.return_value = {"total": 0}
        result = dpsk.list_devices("pool-1", "pp-1")
        assert result == []


class TestAddDevices:
    """Tests for DPSK.add_devices()."""

    def test_posts_devices(self, dpsk):
        devices = [{"mac": "AA:BB:CC:DD:EE:FF"}]
        dpsk.client.post.return_value = {"added": 1}
        result = dpsk.add_devices("pool-1", "pp-1", devices)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices",
            {"devices": devices},
        )
        assert result == {"added": 1}


class TestUpdateDevices:
    """Tests for DPSK.update_devices()."""

    def test_patches_devices(self, dpsk):
        devices = [{"mac": "AA:BB:CC:DD:EE:FF", "description": "laptop"}]
        dpsk.client.patch.return_value = {"updated": 1}
        result = dpsk.update_devices("pool-1", "pp-1", devices)
        dpsk.client.patch.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices",
            {"devices": devices},
        )
        assert result == {"updated": 1}


class TestRemoveDevices:
    """Tests for DPSK.remove_devices()."""

    def test_deletes_by_mac(self, dpsk):
        macs = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]
        dpsk.remove_devices("pool-1", "pp-1", macs)
        dpsk.client.delete.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices",
            json_data={"deviceMacs": macs},
        )

    def test_returns_none(self, dpsk):
        result = dpsk.remove_devices("pool-1", "pp-1", ["AA:BB:CC:DD:EE:FF"])
        assert result is None


# ---------------------------------------------------------------------------
# CSV import / export
# ---------------------------------------------------------------------------

class TestImportPassphrasesCsv:
    """Tests for DPSK.import_passphrases_csv()."""

    def test_posts_csv_content(self, dpsk):
        csv = "userName,passphrase\nuser1,secret123\n"
        dpsk.client.post.return_value = {"imported": 1}
        result = dpsk.import_passphrases_csv("pool-1", csv)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/csvFiles",
            data=csv,
            headers={"Content-Type": "text/csv"},
        )
        assert result == {"imported": 1}

    def test_empty_csv(self, dpsk):
        dpsk.client.post.return_value = {"imported": 0}
        result = dpsk.import_passphrases_csv("pool-1", "")
        dpsk.client.post.assert_called_once()
        assert result == {"imported": 0}


class TestExportPassphrasesCsv:
    """Tests for DPSK.export_passphrases_csv()."""

    def test_no_filters(self, dpsk):
        mock_response = MagicMock()
        mock_response.text = "userName,passphrase\nuser1,abc\n"
        dpsk.client.post.return_value = mock_response
        result = dpsk.export_passphrases_csv("pool-1")
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query/csvFiles",
            {},
            raw_response=True,
        )
        assert result == "userName,passphrase\nuser1,abc\n"

    def test_with_filters(self, dpsk):
        mock_response = MagicMock()
        mock_response.text = "data"
        dpsk.client.post.return_value = mock_response
        filters = {"searchString": "guest", "pageSize": 500}
        dpsk.export_passphrases_csv("pool-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query/csvFiles",
            {"searchString": "guest", "pageSize": 500},
            raw_response=True,
        )

    def test_filters_ignores_unknown_keys(self, dpsk):
        mock_response = MagicMock()
        mock_response.text = ""
        dpsk.client.post.return_value = mock_response
        dpsk.export_passphrases_csv("pool-1", filters={"page": 0, "junk": True})
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query/csvFiles",
            {"page": 0},
            raw_response=True,
        )

    def test_filters_skips_none_values(self, dpsk):
        mock_response = MagicMock()
        mock_response.text = ""
        dpsk.client.post.return_value = mock_response
        dpsk.export_passphrases_csv("pool-1", filters={"page": 0, "sortField": None})
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/query/csvFiles",
            {"page": 0},
            raw_response=True,
        )

    def test_returns_string(self, dpsk):
        mock_response = MagicMock()
        mock_response.text = "col1,col2\nval1,val2\n"
        dpsk.client.post.return_value = mock_response
        result = dpsk.export_passphrases_csv("pool-1")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Constructor / init
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# list_all_passphrases
# ---------------------------------------------------------------------------

class TestListAllPassphrases:
    """Tests for DPSK.list_all_passphrases()."""

    def test_single_page(self, dpsk):
        dpsk.client.get.return_value = {
            "content": [{"id": "pp-1"}, {"id": "pp-2"}],
            "totalElements": 2,
        }
        result = dpsk.list_all_passphrases("pool-1")
        dpsk.client.get.assert_called_once_with(
            "/dpskServices/pool-1/passphrases",
            params={"page": 0, "size": 100},
        )
        assert result == [{"id": "pp-1"}, {"id": "pp-2"}]

    def test_multiple_pages(self, dpsk):
        dpsk.client.get.side_effect = [
            {"content": [{"id": "pp-1"}], "totalElements": 2},
            {"content": [{"id": "pp-2"}], "totalElements": 2},
        ]
        result = dpsk.list_all_passphrases("pool-1", page_size=1)
        assert result == [{"id": "pp-1"}, {"id": "pp-2"}]
        assert dpsk.client.get.call_count == 2

    def test_list_response(self, dpsk):
        dpsk.client.get.return_value = [{"id": "pp-1"}]
        result = dpsk.list_all_passphrases("pool-1")
        assert result == [{"id": "pp-1"}]

    def test_empty_result(self, dpsk):
        dpsk.client.get.return_value = {"content": [], "totalElements": 0}
        result = dpsk.list_all_passphrases("pool-1")
        assert result == []

    def test_passes_kwargs(self, dpsk):
        dpsk.client.get.return_value = {"content": [], "totalElements": 0}
        dpsk.list_all_passphrases("pool-1", sort="name,asc")
        call_params = dpsk.client.get.call_args[1]["params"]
        assert call_params["sort"] == "name,asc"


# ---------------------------------------------------------------------------
# patch_passphrase
# ---------------------------------------------------------------------------

class TestPatchPassphrase:
    """Tests for DPSK.patch_passphrase()."""

    def test_patches_with_updates(self, dpsk):
        updates = {"userName": "new-name"}
        dpsk.client.patch.return_value = {"id": "pp-1", "userName": "new-name"}
        result = dpsk.patch_passphrase("pool-1", "pp-1", updates)
        dpsk.client.patch.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1", updates
        )
        assert result["userName"] == "new-name"

    def test_returns_api_response(self, dpsk):
        expected = {"id": "pp-1", "status": "updated"}
        dpsk.client.patch.return_value = expected
        result = dpsk.patch_passphrase("pool-1", "pp-1", {"status": "active"})
        assert result == expected


# ---------------------------------------------------------------------------
# query_devices
# ---------------------------------------------------------------------------

class TestQueryDevices:
    """Tests for DPSK.query_devices()."""

    def test_no_filters(self, dpsk):
        dpsk.client.post.return_value = {"data": [], "totalCount": 0}
        result = dpsk.query_devices("pool-1", "pp-1")
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices/query", {}
        )
        assert result == {"data": [], "totalCount": 0}

    def test_with_filters(self, dpsk):
        filters = {"page": 0, "pageSize": 50, "searchString": "laptop"}
        dpsk.client.post.return_value = {"data": [{"mac": "AA:BB:CC:DD:EE:FF"}]}
        dpsk.query_devices("pool-1", "pp-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices/query", filters
        )

    def test_filters_ignores_unknown_keys(self, dpsk):
        filters = {"page": 0, "bogus": "nope"}
        dpsk.client.post.return_value = {"data": []}
        dpsk.query_devices("pool-1", "pp-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices/query", {"page": 0}
        )

    def test_filters_skips_none_values(self, dpsk):
        filters = {"page": 0, "sortOrder": None}
        dpsk.client.post.return_value = {"data": []}
        dpsk.query_devices("pool-1", "pp-1", filters=filters)
        dpsk.client.post.assert_called_once_with(
            "/dpskServices/pool-1/passphrases/pp-1/devices/query", {"page": 0}
        )


class TestInit:
    """Tests for DPSK.__init__()."""

    def test_stores_client_reference(self):
        client = MagicMock()
        dpsk = DPSK(client)
        assert dpsk.client is client
