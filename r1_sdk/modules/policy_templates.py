"""
Policy Templates module for the R1 API.

This module handles policy template queries and policy CRUD operations
within templates (e.g. RADIUS policies).
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PolicyTemplates:
    """
    Policy Templates API module.

    Manages policy templates and their associated policies.
    Template IDs are int (int64), policy IDs are str (UUID).
    """

    def __init__(self, client):
        """
        Initialize the PolicyTemplates module.

        Args:
            client: R1Client instance
        """
        self.client = client

    # ── Template queries ────────────────────────────────────────

    def query_templates(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query policy templates.

        Args:
            filters: Query parameters (page, pageSize, filters, etc.)

        Returns:
            Dict containing paginated template results
        """
        data = dict(filters) if filters else {}
        logger.debug(f"Querying policy templates: {data}")
        return self.client.post("/policyTemplates/query", data=data)

    def list_all_templates(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all policy templates using auto-pagination. Returns flat list."""
        return self.client.paginate_query("/policyTemplates/query", kwargs or None)

    def get_template(self, template_id: int) -> Dict[str, Any]:
        """
        Get a policy template by ID.

        Args:
            template_id: Template ID (int)

        Returns:
            Template details
        """
        logger.debug(f"Getting policy template: {template_id}")
        return self.client.get(f"/policyTemplates/{template_id}")

    def list_template_attributes(self, template_id: int) -> Any:
        """
        List attributes for a policy template.

        Args:
            template_id: Template ID (int)

        Returns:
            List of template attributes
        """
        logger.debug(f"Listing attributes for template: {template_id}")
        return self.client.get(f"/policyTemplates/{template_id}/attributes")

    # ── Policy queries ──────────────────────────────────────────

    def query_policies(self, template_id: int, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query policies within a template.

        Args:
            template_id: Template ID (int)
            filters: Query parameters (page, pageSize, filters, etc.)

        Returns:
            Dict containing paginated policy results
        """
        data = dict(filters) if filters else {}
        logger.debug(f"Querying policies for template {template_id}: {data}")
        return self.client.post(f"/policyTemplates/{template_id}/policies/query", data=data)

    def list_all_policies(self, template_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all policies for a template using auto-pagination. Returns flat list."""
        return self.client.paginate_query(
            f"/policyTemplates/{template_id}/policies/query", kwargs or None
        )

    # ── Policy CRUD ─────────────────────────────────────────────

    def get_policy(self, template_id: int, policy_id: str) -> Dict[str, Any]:
        """
        Get a policy by ID.

        Args:
            template_id: Template ID (int)
            policy_id: Policy ID (str/UUID)

        Returns:
            Policy details
        """
        logger.debug(f"Getting policy {policy_id} from template {template_id}")
        return self.client.get(f"/policyTemplates/{template_id}/policies/{policy_id}")

    def create_policy(
        self,
        template_id: int,
        name: str,
        policy_type: str,
        description: Optional[str] = None,
        on_match_response: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a policy within a template.

        Uses synchronous content-type header to get 201 instead of 202.

        Args:
            template_id: Template ID (int)
            name: Policy name
            policy_type: Policy type (e.g. "RADIUS")
            description: Optional description
            on_match_response: Optional RADIUS attribute group ID for on-match response
            **kwargs: Additional policy properties

        Returns:
            Created policy details
        """
        payload: Dict[str, Any] = {"name": name, "policyType": policy_type, **kwargs}
        if description:
            payload["description"] = description
        if on_match_response:
            payload["onMatchResponse"] = on_match_response

        logger.debug(f"Creating policy in template {template_id}: {payload}")

        # Use synchronous content-type to get a 201 response.
        # Must use client.request() directly with data= (not json_data=)
        # because json_data= causes requests to override Content-Type.
        return self.client.request(
            "POST",
            f"/policyTemplates/{template_id}/policies",
            data=json.dumps(payload),
            headers={"Content-Type": "application/ruckus.one.v1-synchronous+json"},
        )

    def update_policy(self, template_id: int, policy_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a policy.

        Args:
            template_id: Template ID (int)
            policy_id: Policy ID (str/UUID)
            **kwargs: Fields to update

        Returns:
            Updated policy details
        """
        logger.debug(f"Updating policy {policy_id} in template {template_id}: {kwargs}")
        return self.client.patch(f"/policyTemplates/{template_id}/policies/{policy_id}", data=kwargs)

    def delete_policy(self, template_id: int, policy_id: str) -> None:
        """
        Delete a policy.

        Args:
            template_id: Template ID (int)
            policy_id: Policy ID (str/UUID)
        """
        logger.debug(f"Deleting policy {policy_id} from template {template_id}")
        self.client.delete(f"/policyTemplates/{template_id}/policies/{policy_id}")
