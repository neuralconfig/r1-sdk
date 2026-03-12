"""
MAC Registration Pools module for the R1 API.

This module handles MAC registration pool management — pools, registrations,
CSV import, and policy set associations.

Mutation endpoints use the v1.1 async pattern (Accept: application/vnd.ruckus.v1.1+json)
which returns 202 Accepted with a requestId. Read endpoints are synchronous.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Header for v1.1 async mutation endpoints
_V11_ACCEPT = {"Accept": "application/vnd.ruckus.v1.1+json"}


class MacRegistrationPools:
    """
    MAC Registration Pools API module.

    Manages MAC registration pools and their registrations.
    """

    def __init__(self, client):
        """
        Initialize the MacRegistrationPools module.

        Args:
            client: R1Client instance
        """
        self.client = client

    # ── Pool CRUD ──────────────────────────────────────────────

    def query(self, filters: Optional[Dict[str, Any]] = None,
              page: int = 0, size: int = 20, **params) -> Dict[str, Any]:
        """
        Search MAC registration pools by criteria.

        The POST /query endpoint takes a SearchDto body (dataOption,
        searchCriteriaList) and pagination as **query params** (page, size),
        unlike most other R1 query endpoints.

        Args:
            filters: Search body (dataOption, searchCriteriaList)
            page: Page number (query param, default 0)
            size: Page size (query param, default 20)
            **params: Additional query parameters (sort, etc.)

        Returns:
            Dict containing paginated pool results
        """
        data = dict(filters) if filters else {}
        query_params = {"page": page, "size": size, **params}
        logger.debug(f"Querying MAC registration pools: {data}")
        return self.client.post(
            "/macRegistrationPools/query",
            data=data,
            params=query_params
        )

    def list_all(self, page_size: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all MAC registration pools via GET with pagination. Returns flat list."""
        all_pools: list = []
        page = 0
        while True:
            params = {"page": page, "size": page_size, **kwargs}
            logger.debug(f"Listing MAC registration pools page {page}")
            result = self.client.get("/macRegistrationPools", params=params)
            if isinstance(result, list):
                all_pools.extend(result)
                break
            if isinstance(result, dict):
                items = result.get("content", result.get("data", []))
                all_pools.extend(items)
                total = result.get("totalElements", result.get("totalCount", 0))
                if len(all_pools) >= total or not items:
                    break
                page += 1
            else:
                break
        return all_pools

    def get(self, pool_id: str) -> Dict[str, Any]:
        """
        Get a MAC registration pool by ID.

        Args:
            pool_id: Pool ID

        Returns:
            Pool details
        """
        logger.debug(f"Getting MAC registration pool: {pool_id}")
        return self.client.get(f"/macRegistrationPools/{pool_id}")

    def create(self, identity_group_id: str, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a MAC registration pool under an identity group.

        This endpoint is natively async (202 Accepted) and non-deprecated.

        Args:
            identity_group_id: Identity group ID to create the pool under
            name: Pool name
            **kwargs: Additional pool properties

        Returns:
            Async response with requestId
        """
        data = {"name": name, **kwargs}
        logger.debug(f"Creating MAC registration pool '{name}' in group {identity_group_id}")
        return self.client.post(
            f"/identityGroups/{identity_group_id}/macRegistrationPools",
            data=data
        )

    def create_standalone(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a standalone MAC registration pool (not under an identity group).

        Note: This endpoint uses v1.1 headers. The standalone creation endpoint
        is scheduled for migration to v1.1 by 2026-08-31.

        Args:
            name: Pool name
            **kwargs: Additional pool properties

        Returns:
            Async response with requestId
        """
        data = {"name": name, **kwargs}
        logger.debug(f"Creating standalone MAC registration pool '{name}'")
        return self.client.post(
            "/macRegistrationPools",
            data=data,
            headers=_V11_ACCEPT
        )

    def update(self, pool_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID
            **kwargs: Fields to update

        Returns:
            Async response with requestId
        """
        logger.debug(f"Updating MAC registration pool {pool_id}: {kwargs}")
        return self.client.patch(
            f"/macRegistrationPools/{pool_id}",
            data=kwargs,
            headers=_V11_ACCEPT
        )

    def delete(self, pool_id: str) -> Dict[str, Any]:
        """
        Delete a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID

        Returns:
            Async response with requestId
        """
        logger.debug(f"Deleting MAC registration pool: {pool_id}")
        return self.client.delete(
            f"/macRegistrationPools/{pool_id}",
            headers=_V11_ACCEPT
        )

    # ── Registration CRUD ──────────────────────────────────────

    def query_registrations(self, pool_id: str, filters: Optional[Dict[str, Any]] = None,
                            page: int = 0, size: int = 20, **params) -> Dict[str, Any]:
        """
        Search registrations in a MAC registration pool.

        Like the pool query endpoint, pagination is via query params.

        Args:
            pool_id: Pool ID
            filters: Search body (dataOption, searchCriteriaList)
            page: Page number (query param, default 0)
            size: Page size (query param, default 20)
            **params: Additional query parameters (sort, etc.)

        Returns:
            Dict containing paginated registration results
        """
        data = dict(filters) if filters else {}
        query_params = {"page": page, "size": size, **params}
        logger.debug(f"Querying registrations for pool {pool_id}: {data}")
        return self.client.post(
            f"/macRegistrationPools/{pool_id}/registrations/query",
            data=data,
            params=query_params
        )

    def list_all_registrations(self, pool_id: str, page_size: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all registrations in a pool via GET with pagination. Returns flat list."""
        all_regs: list = []
        page = 0
        while True:
            params = {"page": page, "size": page_size, **kwargs}
            logger.debug(f"Listing registrations for pool {pool_id} page {page}")
            result = self.client.get(
                f"/macRegistrationPools/{pool_id}/registrations", params=params
            )
            if isinstance(result, list):
                all_regs.extend(result)
                break
            if isinstance(result, dict):
                items = result.get("content", result.get("data", []))
                all_regs.extend(items)
                total = result.get("totalElements", result.get("totalCount", 0))
                if len(all_regs) >= total or not items:
                    break
                page += 1
            else:
                break
        return all_regs

    def get_registration(self, pool_id: str, reg_id: str) -> Dict[str, Any]:
        """
        Get a single registration by ID.

        Args:
            pool_id: Pool ID
            reg_id: Registration ID

        Returns:
            Registration details
        """
        logger.debug(f"Getting registration {reg_id} from pool {pool_id}")
        return self.client.get(f"/macRegistrationPools/{pool_id}/registrations/{reg_id}")

    def create_registration(self, pool_id: str, mac_address: str, **kwargs) -> Dict[str, Any]:
        """
        Create a registration in a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID
            mac_address: MAC address to register
            **kwargs: Additional registration properties

        Returns:
            Async response with requestId
        """
        data = {"macAddress": mac_address, **kwargs}
        logger.debug(f"Creating registration in pool {pool_id}: {mac_address}")
        return self.client.post(
            f"/macRegistrationPools/{pool_id}/registrations",
            data=data,
            headers=_V11_ACCEPT
        )

    def update_registration(self, pool_id: str, reg_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a registration in a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID
            reg_id: Registration ID
            **kwargs: Fields to update

        Returns:
            Async response with requestId
        """
        logger.debug(f"Updating registration {reg_id} in pool {pool_id}: {kwargs}")
        return self.client.patch(
            f"/macRegistrationPools/{pool_id}/registrations/{reg_id}",
            data=kwargs,
            headers=_V11_ACCEPT
        )

    def delete_registration(self, pool_id: str, reg_id: str) -> Dict[str, Any]:
        """
        Delete a registration from a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID
            reg_id: Registration ID

        Returns:
            Async response with requestId
        """
        logger.debug(f"Deleting registration {reg_id} from pool {pool_id}")
        return self.client.delete(
            f"/macRegistrationPools/{pool_id}/registrations/{reg_id}",
            headers=_V11_ACCEPT
        )

    def delete_registrations(self, pool_id: str, reg_ids: List[str]) -> Dict[str, Any]:
        """
        Bulk delete registrations from a MAC registration pool (v1.1 async).

        Args:
            pool_id: Pool ID
            reg_ids: List of registration IDs to delete

        Returns:
            Async response with requestId
        """
        logger.debug(f"Bulk deleting {len(reg_ids)} registrations from pool {pool_id}")
        return self.client.delete(
            f"/macRegistrationPools/{pool_id}/registrations",
            json_data={"ids": reg_ids},
            headers=_V11_ACCEPT
        )

    def import_csv(self, pool_id: str, csv_bytes: bytes) -> Dict[str, Any]:
        """
        Import registrations from CSV into a pool (v1.1 async, multipart).

        Args:
            pool_id: Pool ID
            csv_bytes: CSV file content as bytes

        Returns:
            Async response with requestId
        """
        files = {'file': ('registrations.csv', csv_bytes, 'text/csv')}
        logger.debug(f"Importing CSV registrations into pool {pool_id}")
        return self.client.request(
            'POST',
            f"/macRegistrationPools/{pool_id}/registrations/csvFile",
            files=files,
            headers=_V11_ACCEPT
        )

    # ── Policy Set Associations ────────────────────────────────

    def associate_policy_set(self, pool_id: str, policy_set_id: str) -> Dict[str, Any]:
        """
        Associate a policy set with a MAC registration pool (async 202).

        Args:
            pool_id: Pool ID
            policy_set_id: Policy set ID

        Returns:
            Async response with requestId
        """
        logger.debug(f"Associating policy set {policy_set_id} with pool {pool_id}")
        return self.client.put(f"/macRegistrationPools/{pool_id}/policySets/{policy_set_id}")

    def remove_policy_set(self, pool_id: str, policy_set_id: str) -> Dict[str, Any]:
        """
        Remove a policy set association from a MAC registration pool (async 202).

        Args:
            pool_id: Pool ID
            policy_set_id: Policy set ID

        Returns:
            Async response with requestId
        """
        logger.debug(f"Removing policy set {policy_set_id} from pool {pool_id}")
        return self.client.delete(f"/macRegistrationPools/{pool_id}/policySets/{policy_set_id}")
