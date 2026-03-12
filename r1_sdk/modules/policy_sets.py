"""
Policy Sets module for the R1 API.

This module handles adaptive policy set management — CRUD operations,
prioritized policy assignments, and assignment queries.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PolicySets:
    """
    Policy Sets API module.

    Manages adaptive policy sets and their prioritized policies.
    """

    def __init__(self, client):
        """
        Initialize the PolicySets module.

        Args:
            client: R1Client instance
        """
        self.client = client

    # ── Policy Set CRUD ────────────────────────────────────────

    def query(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query policy sets.

        Args:
            filters: Query parameters (page, pageSize, filters, etc.)

        Returns:
            Dict containing paginated policy set results
        """
        data = dict(filters) if filters else {}
        logger.debug(f"Querying policy sets: {data}")
        return self.client.post("/policySets/query", data=data)

    def list_all(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all policy sets using auto-pagination. Returns flat list."""
        return self.client.paginate_query("/policySets/query", kwargs or None)

    def get(self, policy_set_id: str) -> Dict[str, Any]:
        """
        Get a policy set by ID.

        Args:
            policy_set_id: Policy set ID

        Returns:
            Policy set details
        """
        logger.debug(f"Getting policy set: {policy_set_id}")
        return self.client.get(f"/policySets/{policy_set_id}")

    def create(self, name: str, description: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Create a new policy set.

        Args:
            name: Policy set name
            description: Optional description
            **kwargs: Additional policy set properties

        Returns:
            Created policy set details
        """
        data = {"name": name, **kwargs}
        if description:
            data["description"] = description
        logger.debug(f"Creating policy set: {data}")
        return self.client.post("/policySets", data=data)

    def update(self, policy_set_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a policy set.

        Args:
            policy_set_id: Policy set ID
            **kwargs: Fields to update

        Returns:
            Updated policy set details
        """
        logger.debug(f"Updating policy set {policy_set_id}: {kwargs}")
        return self.client.patch(f"/policySets/{policy_set_id}", data=kwargs)

    def delete(self, policy_set_id: str) -> None:
        """
        Delete a policy set.

        Args:
            policy_set_id: Policy set ID
        """
        logger.debug(f"Deleting policy set: {policy_set_id}")
        self.client.delete(f"/policySets/{policy_set_id}")

    # ── Prioritized Policies ───────────────────────────────────

    def list_policies(self, policy_set_id: str) -> List[Dict[str, Any]]:
        """
        List prioritized policies in a policy set.

        Args:
            policy_set_id: Policy set ID

        Returns:
            List of prioritized policies
        """
        logger.debug(f"Listing policies for set {policy_set_id}")
        result = self.client.get(f"/policySets/{policy_set_id}/prioritizedPolicies")
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return result.get('data', result.get('content', []))
        return []

    def add_policy(self, policy_set_id: str, policy_id: str, **kwargs) -> Dict[str, Any]:
        """
        Add a policy to a policy set.

        Args:
            policy_set_id: Policy set ID
            policy_id: Policy ID to add
            **kwargs: Additional properties (e.g., priority)

        Returns:
            Operation result
        """
        logger.debug(f"Adding policy {policy_id} to set {policy_set_id}")
        return self.client.put(
            f"/policySets/{policy_set_id}/prioritizedPolicies/{policy_id}",
            data=kwargs if kwargs else {}
        )

    def remove_policy(self, policy_set_id: str, policy_id: str) -> None:
        """
        Remove a policy from a policy set.

        Args:
            policy_set_id: Policy set ID
            policy_id: Policy ID to remove
        """
        logger.debug(f"Removing policy {policy_id} from set {policy_set_id}")
        self.client.delete(f"/policySets/{policy_set_id}/prioritizedPolicies/{policy_id}")

    # ── Assignments ────────────────────────────────────────────

    def get_assignments(self, policy_set_id: str) -> Dict[str, Any]:
        """
        Get assignments for a policy set.

        Args:
            policy_set_id: Policy set ID

        Returns:
            Assignment details
        """
        logger.debug(f"Getting assignments for policy set {policy_set_id}")
        return self.client.get(f"/policySets/{policy_set_id}/assignments")
