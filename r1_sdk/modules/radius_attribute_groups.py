"""
RADIUS Attribute Groups module for the R1 API.

This module handles RADIUS attribute group management — CRUD operations
and reference data for available attributes and vendors.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RadiusAttributeGroups:
    """
    RADIUS Attribute Groups API module.

    Manages RADIUS attribute groups and provides reference data
    for available RADIUS attributes and vendors.
    """

    def __init__(self, client):
        """
        Initialize the RadiusAttributeGroups module.

        Args:
            client: R1Client instance
        """
        self.client = client

    # ── Group CRUD ─────────────────────────────────────────────

    def query(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query RADIUS attribute groups.

        Args:
            filters: Query parameters (page, pageSize, filters, etc.)

        Returns:
            Dict containing paginated results
        """
        data = dict(filters) if filters else {}
        logger.debug(f"Querying RADIUS attribute groups: {data}")
        return self.client.post("/radiusAttributeGroups/query", data=data)

    def list_all(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all RADIUS attribute groups using auto-pagination. Returns flat list."""
        return self.client.paginate_query("/radiusAttributeGroups/query", kwargs or None)

    def get(self, group_id: str) -> Dict[str, Any]:
        """
        Get a RADIUS attribute group by ID.

        Args:
            group_id: Group ID

        Returns:
            Group details
        """
        logger.debug(f"Getting RADIUS attribute group: {group_id}")
        return self.client.get(f"/radiusAttributeGroups/{group_id}")

    def create(self, name: str, attribute_assignments: List[Dict[str, Any]],
               **kwargs) -> Dict[str, Any]:
        """
        Create a new RADIUS attribute group.

        Args:
            name: Group name
            attribute_assignments: List of attribute assignment dicts
            **kwargs: Additional group properties

        Returns:
            Created group details
        """
        data = {"name": name, "attributeAssignments": attribute_assignments, **kwargs}
        logger.debug(f"Creating RADIUS attribute group: {name}")
        return self.client.post("/radiusAttributeGroups", data=data)

    def update(self, group_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a RADIUS attribute group.

        Args:
            group_id: Group ID
            **kwargs: Fields to update

        Returns:
            Updated group details
        """
        logger.debug(f"Updating RADIUS attribute group {group_id}: {kwargs}")
        return self.client.patch(f"/radiusAttributeGroups/{group_id}", data=kwargs)

    def delete(self, group_id: str) -> None:
        """
        Delete a RADIUS attribute group.

        Args:
            group_id: Group ID
        """
        logger.debug(f"Deleting RADIUS attribute group: {group_id}")
        self.client.delete(f"/radiusAttributeGroups/{group_id}")

    # ── Reference Data ─────────────────────────────────────────

    def list_attributes(self, **kwargs) -> Any:
        """
        List available RADIUS attributes.

        Args:
            **kwargs: Optional query parameters

        Returns:
            List of available RADIUS attributes
        """
        logger.debug("Listing RADIUS attributes")
        return self.client.get("/radiusAttributes", params=kwargs if kwargs else None)

    def list_vendors(self) -> Any:
        """
        List RADIUS attribute vendors.

        Returns:
            List of RADIUS attribute vendors
        """
        logger.debug("Listing RADIUS attribute vendors")
        return self.client.get("/radiusAttributes/vendors")
