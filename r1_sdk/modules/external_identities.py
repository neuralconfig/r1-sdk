"""
External Identities module for the R1 API.

This module provides read-only access to external identities (e.g., identities
sourced from external authentication providers).
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExternalIdentities:
    """
    External Identities API module (read-only).

    Provides query access to external identities.
    """

    def __init__(self, client):
        """
        Initialize the ExternalIdentities module.

        Args:
            client: R1Client instance
        """
        self.client = client

    def query(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query external identities.

        Args:
            filters: Query parameters (page, pageSize, filters, etc.)

        Returns:
            Dict containing paginated external identity results
        """
        data = dict(filters) if filters else {}
        logger.debug(f"Querying external identities: {data}")
        return self.client.post("/externalIdentities/query", data=data)

    def list_all(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all external identities using auto-pagination. Returns flat list."""
        return self.client.paginate_query("/externalIdentities/query", kwargs or None)
