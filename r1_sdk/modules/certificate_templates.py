"""
Certificate Templates module for the R1 API.

This module handles certificate template operations such as querying
and retrieving templates linked to WiFi networks.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CertificateTemplates:
    """
    Certificate Templates API module.

    Handles operations related to certificate templates in the R1 API.
    """

    def __init__(self, client):
        self.client = client

    def query(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query certificate templates with pagination.

        Args:
            query_data: Query parameters including pagination, filters, etc.

        Returns:
            Dict containing templates and pagination information
        """
        if query_data is None:
            query_data = {}
        return self.client.post("/certificateTemplates/query", data=query_data)

    def get(self, template_id: str) -> Dict[str, Any]:
        """
        Get a certificate template by ID.

        Args:
            template_id: ID of the template to retrieve

        Returns:
            Dict containing the template details
        """
        return self.client.get(f"/certificateTemplates/{template_id}")

    def get_for_wifi_network(self, wlan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the certificate template linked to a WiFi network.

        Queries all templates and returns the one whose networkIds contains
        the given WLAN ID, or None if not found.

        Args:
            wlan_id: WiFi network ID to filter by

        Returns:
            Dict containing the matching template, or None
        """
        result = self.query()
        for template in result.get("data", []):
            if wlan_id in template.get("networkIds", []):
                return template
        return None
