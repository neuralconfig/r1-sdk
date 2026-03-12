"""Comprehensive unit tests for the MacRegistrationPools module."""

from unittest.mock import MagicMock

import pytest

from r1_sdk.modules.mac_registration_pools import MacRegistrationPools, _V11_ACCEPT


@pytest.fixture
def mac_pools():
    client = MagicMock()
    return MacRegistrationPools(client)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestInit:
    def test_stores_client_reference(self):
        client = MagicMock()
        mp = MacRegistrationPools(client)
        assert mp.client is client


# ---------------------------------------------------------------------------
# query()
# ---------------------------------------------------------------------------

class TestQuery:
    def test_default_params(self, mac_pools):
        mac_pools.client.post.return_value = {"data": []}
        mac_pools.query()
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools/query",
            data={},
            params={"page": 0, "size": 20},
        )

    def test_with_filters(self, mac_pools):
        filters = {"searchCriteriaList": [{"key": "name", "value": "Test"}]}
        mac_pools.client.post.return_value = {"data": []}
        mac_pools.query(filters=filters, page=1, size=50)
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools/query",
            data=filters,
            params={"page": 1, "size": 50},
        )

    def test_extra_params(self, mac_pools):
        mac_pools.client.post.return_value = {}
        mac_pools.query(sort="name,asc")
        call_kwargs = mac_pools.client.post.call_args[1]
        assert call_kwargs["params"]["sort"] == "name,asc"


# ---------------------------------------------------------------------------
# list_all()
# ---------------------------------------------------------------------------

class TestListAll:
    def test_single_page(self, mac_pools):
        mac_pools.client.get.return_value = {
            "content": [{"id": "p1"}],
            "totalElements": 1,
        }
        result = mac_pools.list_all()
        assert result == [{"id": "p1"}]

    def test_multiple_pages(self, mac_pools):
        mac_pools.client.get.side_effect = [
            {"content": [{"id": "p1"}], "totalElements": 2},
            {"content": [{"id": "p2"}], "totalElements": 2},
        ]
        result = mac_pools.list_all(page_size=1)
        assert result == [{"id": "p1"}, {"id": "p2"}]

    def test_list_response(self, mac_pools):
        mac_pools.client.get.return_value = [{"id": "p1"}]
        result = mac_pools.list_all()
        assert result == [{"id": "p1"}]

    def test_empty(self, mac_pools):
        mac_pools.client.get.return_value = {"content": [], "totalElements": 0}
        assert mac_pools.list_all() == []


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_gets_by_id(self, mac_pools):
        expected = {"id": "p1", "name": "Pool 1"}
        mac_pools.client.get.return_value = expected
        result = mac_pools.get("p1")
        mac_pools.client.get.assert_called_once_with("/macRegistrationPools/p1")
        assert result == expected


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------

class TestCreate:
    def test_creates_under_identity_group(self, mac_pools):
        mac_pools.client.post.return_value = {"requestId": "r1"}
        result = mac_pools.create("ig-1", "Pool1")
        mac_pools.client.post.assert_called_once_with(
            "/identityGroups/ig-1/macRegistrationPools",
            data={"name": "Pool1"},
        )
        assert result["requestId"] == "r1"

    def test_with_kwargs(self, mac_pools):
        mac_pools.client.post.return_value = {}
        mac_pools.create("ig-1", "Pool1", description="Test")
        call_data = mac_pools.client.post.call_args[1]["data"]
        assert call_data["description"] == "Test"


# ---------------------------------------------------------------------------
# create_standalone()
# ---------------------------------------------------------------------------

class TestCreateStandalone:
    def test_posts_to_correct_endpoint(self, mac_pools):
        mac_pools.client.post.return_value = {"requestId": "r1"}
        result = mac_pools.create_standalone("Standalone Pool")
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools",
            data={"name": "Standalone Pool"},
            headers=_V11_ACCEPT,
        )
        assert result["requestId"] == "r1"

    def test_with_kwargs(self, mac_pools):
        mac_pools.client.post.return_value = {}
        mac_pools.create_standalone("Pool", description="Test", maxSize=500)
        call_data = mac_pools.client.post.call_args[1]["data"]
        assert call_data == {"name": "Pool", "description": "Test", "maxSize": 500}

    def test_uses_v11_headers(self, mac_pools):
        mac_pools.client.post.return_value = {}
        mac_pools.create_standalone("Pool")
        call_kwargs = mac_pools.client.post.call_args[1]
        assert call_kwargs["headers"] == _V11_ACCEPT


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_patches_with_v11(self, mac_pools):
        mac_pools.client.patch.return_value = {"requestId": "r1"}
        mac_pools.update("p1", name="Renamed")
        mac_pools.client.patch.assert_called_once_with(
            "/macRegistrationPools/p1",
            data={"name": "Renamed"},
            headers=_V11_ACCEPT,
        )


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    def test_deletes_with_v11(self, mac_pools):
        mac_pools.client.delete.return_value = {"requestId": "r1"}
        mac_pools.delete("p1")
        mac_pools.client.delete.assert_called_once_with(
            "/macRegistrationPools/p1",
            headers=_V11_ACCEPT,
        )


# ---------------------------------------------------------------------------
# query_registrations()
# ---------------------------------------------------------------------------

class TestQueryRegistrations:
    def test_default_params(self, mac_pools):
        mac_pools.client.post.return_value = {"data": []}
        mac_pools.query_registrations("p1")
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools/p1/registrations/query",
            data={},
            params={"page": 0, "size": 20},
        )

    def test_with_filters(self, mac_pools):
        filters = {"searchCriteriaList": [{"key": "mac", "value": "AA"}]}
        mac_pools.client.post.return_value = {}
        mac_pools.query_registrations("p1", filters=filters, page=2, size=50)
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools/p1/registrations/query",
            data=filters,
            params={"page": 2, "size": 50},
        )


# ---------------------------------------------------------------------------
# list_all_registrations()
# ---------------------------------------------------------------------------

class TestListAllRegistrations:
    def test_single_page(self, mac_pools):
        mac_pools.client.get.return_value = {
            "content": [{"id": "r1"}],
            "totalElements": 1,
        }
        result = mac_pools.list_all_registrations("p1")
        assert result == [{"id": "r1"}]

    def test_multiple_pages(self, mac_pools):
        mac_pools.client.get.side_effect = [
            {"content": [{"id": "r1"}], "totalElements": 2},
            {"content": [{"id": "r2"}], "totalElements": 2},
        ]
        result = mac_pools.list_all_registrations("p1", page_size=1)
        assert result == [{"id": "r1"}, {"id": "r2"}]


# ---------------------------------------------------------------------------
# get_registration()
# ---------------------------------------------------------------------------

class TestGetRegistration:
    def test_gets_by_id(self, mac_pools):
        expected = {"id": "r1", "macAddress": "AA-BB-CC-DD-EE-FF"}
        mac_pools.client.get.return_value = expected
        result = mac_pools.get_registration("p1", "r1")
        mac_pools.client.get.assert_called_once_with(
            "/macRegistrationPools/p1/registrations/r1"
        )
        assert result == expected


# ---------------------------------------------------------------------------
# create_registration()
# ---------------------------------------------------------------------------

class TestCreateRegistration:
    def test_creates_with_v11(self, mac_pools):
        mac_pools.client.post.return_value = {"requestId": "r1"}
        mac_pools.create_registration("p1", "AA-BB-CC-DD-EE-FF")
        mac_pools.client.post.assert_called_once_with(
            "/macRegistrationPools/p1/registrations",
            data={"macAddress": "AA-BB-CC-DD-EE-FF"},
            headers=_V11_ACCEPT,
        )

    def test_with_kwargs(self, mac_pools):
        mac_pools.client.post.return_value = {}
        mac_pools.create_registration("p1", "AA-BB-CC-DD-EE-FF", description="Test")
        call_data = mac_pools.client.post.call_args[1]["data"]
        assert call_data["description"] == "Test"


# ---------------------------------------------------------------------------
# update_registration()
# ---------------------------------------------------------------------------

class TestUpdateRegistration:
    def test_patches_with_v11(self, mac_pools):
        mac_pools.client.patch.return_value = {"requestId": "r1"}
        mac_pools.update_registration("p1", "r1", description="Updated")
        mac_pools.client.patch.assert_called_once_with(
            "/macRegistrationPools/p1/registrations/r1",
            data={"description": "Updated"},
            headers=_V11_ACCEPT,
        )


# ---------------------------------------------------------------------------
# delete_registration()
# ---------------------------------------------------------------------------

class TestDeleteRegistration:
    def test_deletes_with_v11(self, mac_pools):
        mac_pools.client.delete.return_value = {"requestId": "r1"}
        mac_pools.delete_registration("p1", "r1")
        mac_pools.client.delete.assert_called_once_with(
            "/macRegistrationPools/p1/registrations/r1",
            headers=_V11_ACCEPT,
        )


# ---------------------------------------------------------------------------
# delete_registrations()
# ---------------------------------------------------------------------------

class TestDeleteRegistrations:
    def test_bulk_deletes_with_v11(self, mac_pools):
        mac_pools.client.delete.return_value = {"requestId": "r1"}
        mac_pools.delete_registrations("p1", ["r1", "r2"])
        mac_pools.client.delete.assert_called_once_with(
            "/macRegistrationPools/p1/registrations",
            json_data={"ids": ["r1", "r2"]},
            headers=_V11_ACCEPT,
        )


# ---------------------------------------------------------------------------
# import_csv()
# ---------------------------------------------------------------------------

class TestImportCsv:
    def test_posts_multipart_with_v11(self, mac_pools):
        mac_pools.client.request.return_value = {"requestId": "r1"}
        csv_data = b"mac,description\nAA-BB-CC-DD-EE-FF,Test\n"
        result = mac_pools.import_csv("p1", csv_data)
        mac_pools.client.request.assert_called_once()
        call_args = mac_pools.client.request.call_args
        assert call_args[0][0] == 'POST'
        assert call_args[0][1] == "/macRegistrationPools/p1/registrations/csvFile"
        assert result["requestId"] == "r1"


# ---------------------------------------------------------------------------
# associate_policy_set()
# ---------------------------------------------------------------------------

class TestAssociatePolicySet:
    def test_puts_correct_url(self, mac_pools):
        mac_pools.client.put.return_value = {"requestId": "r1"}
        mac_pools.associate_policy_set("p1", "ps-1")
        mac_pools.client.put.assert_called_once_with(
            "/macRegistrationPools/p1/policySets/ps-1"
        )


# ---------------------------------------------------------------------------
# remove_policy_set()
# ---------------------------------------------------------------------------

class TestRemovePolicySet:
    def test_deletes_correct_url(self, mac_pools):
        mac_pools.client.delete.return_value = {"requestId": "r1"}
        mac_pools.remove_policy_set("p1", "ps-1")
        mac_pools.client.delete.assert_called_once_with(
            "/macRegistrationPools/p1/policySets/ps-1"
        )
