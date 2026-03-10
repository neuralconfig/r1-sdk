"""
RADIUS Server Profiles module for the R1 API.

This module handles RADIUS server profile operations such as listing,
querying, and retrieving profiles linked to WiFi networks.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class RadiusServerProfiles:
    """
    RADIUS Server Profiles API module.

    Handles operations related to RADIUS server profiles in the R1 API.
    """

    def __init__(self, client):
        self.client = client

    def list(self) -> List[Dict[str, Any]]:
        """List all RADIUS server profiles."""
        return self.client.get("/radiusServerProfiles")

    def query(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query RADIUS server profiles with pagination.

        Args:
            query_data: Query parameters including pagination, filters, etc.

        Returns:
            Dict containing profiles and pagination information
        """
        if query_data is None:
            query_data = {"pageSize": 100, "page": 0}
        return self.client.post("/radiusServerProfiles/query", data=query_data)

    def get(self, profile_id: str) -> Dict[str, Any]:
        """
        Get a RADIUS server profile by ID.

        Args:
            profile_id: ID of the profile to retrieve

        Returns:
            Dict containing the full profile details (including server IP/port)
        """
        return self.client.get(f"/radiusServerProfiles/{profile_id}")

    def get_for_wifi_network(self, wlan_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get RADIUS server profiles linked to a WiFi network.

        Queries all profiles and filters by wifiNetworkIds containing the
        given WLAN ID.

        Args:
            wlan_id: WiFi network ID to filter by

        Returns:
            Dict with keys 'AUTHENTICATION' and 'ACCOUNTING', each a list
            of matching profiles.
        """
        result = {"AUTHENTICATION": [], "ACCOUNTING": []}
        profiles = self.query({"pageSize": 100, "page": 0})
        for profile in profiles.get("data", []):
            if wlan_id in profile.get("wifiNetworkIds", []):
                profile_type = profile.get("type", "")
                if profile_type in result:
                    result[profile_type].append(profile)
        return result
