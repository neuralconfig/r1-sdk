"""
WiFi Networks module for the R1 API.

This module handles WiFi network operations such as creating, retrieving,
updating, and deploying wireless networks.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


SECURITY_TYPE_MAP = {
    "psk": ("psk", "WPA2Personal"),
    "wpa2-psk": ("psk", "WPA2Personal"),
    "wpa3-psk": ("psk", "WPA3"),
    "wpa23mixed": ("psk", "WPA23Mixed"),
    "open": ("open", "Open"),
    "owe": ("open", "OWE"),
    "wpa2-enterprise": ("aaa", "WPA2Enterprise"),
    "aaa": ("aaa", "WPA2Enterprise"),
    "wpa3-enterprise": ("aaa", "WPA3"),
}

PSK_TYPES = {"psk"}


class WiFiNetworks:
    """
    WiFi Networks API module.

    Handles operations related to wireless networks in the R1 API.
    """

    def __init__(self, client):
        """
        Initialize the WiFiNetworks module.

        Args:
            client: R1Client instance
        """
        self.client = client
    
    def list(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List WLANs with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing WLANs and pagination information
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 0,
                "sortOrder": "ASC"  # API requires uppercase
            }
        
        # Make sure sortOrder is uppercase
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()
        
        logger.debug(f"Querying WLANs with data: {query_data}")
            
        try:
            result = self.client.post("/wifiNetworks/query", data=query_data)
            logger.debug(f"WLAN query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying WLANs: {str(e)}")
            raise
    
    def list_all(self, query_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch all WiFi networks using auto-pagination. Returns flat list."""
        return self.client.paginate_query("/wifiNetworks/query", query_data)

    def get(self, wlan_id: str) -> Dict[str, Any]:
        """
        Retrieve a WLAN by ID.
        
        Args:
            wlan_id: ID of the WLAN to retrieve
            
        Returns:
            Dict containing WLAN details
            
        Raises:
            ResourceNotFoundError: If the WLAN does not exist
        """
        try:
            return self.client.get(f"/wifiNetworks/{wlan_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"WLAN with ID {wlan_id} not found")
    
    def create(self,
              name: str,
              ssid: str,
              security_type: str = "psk",
              passphrase: Optional[str] = None,
              vlan_id: Optional[int] = None,
              hidden: bool = False,
              enabled: bool = True,
              description: Optional[str] = None,
              wlan_options: Optional[Dict[str, Any]] = None,
              advanced_options: Optional[Dict[str, Any]] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Create a new WLAN.

        Args:
            name: Name of the WLAN
            ssid: SSID (network name) of the WLAN
            security_type: Security type key — one of "psk", "wpa2-psk",
                "wpa3-psk", "wpa23mixed", "open", "owe", "wpa2-enterprise",
                "aaa", or "wpa3-enterprise"
            passphrase: WPA passphrase (required for PSK types)
            vlan_id: Optional VLAN ID for the WLAN
            hidden: Whether the SSID is hidden
            enabled: Whether the WLAN is enabled (default True)
            description: Optional description of the WLAN
            wlan_options: Extra keys merged into the ``wlan`` object
            advanced_options: Extra keys merged into
                ``wlan.advancedCustomization``
            **kwargs: Additional top-level properties

        Returns:
            Dict containing the created WLAN details

        Raises:
            ValueError: If *security_type* is unknown or *passphrase* is
                missing for a PSK network.
        """
        key = security_type.lower()
        if key not in SECURITY_TYPE_MAP:
            raise ValueError(
                f"Unknown security_type '{security_type}'. "
                f"Valid options: {', '.join(sorted(SECURITY_TYPE_MAP))}"
            )

        network_type, wlan_security = SECURITY_TYPE_MAP[key]

        if network_type in PSK_TYPES and not passphrase:
            raise ValueError("passphrase is required for PSK security types")

        wlan: Dict[str, Any] = {
            "ssid": ssid,
            "wlanSecurity": wlan_security,
            "enabled": enabled,
        }

        if passphrase and network_type in PSK_TYPES:
            wlan["passphrase"] = passphrase

        if vlan_id is not None:
            wlan["vlanId"] = vlan_id

        if hidden or advanced_options:
            adv: Dict[str, Any] = {}
            if hidden:
                adv["hideSsid"] = True
            if advanced_options:
                adv.update(advanced_options)
            wlan["advancedCustomization"] = adv

        if wlan_options:
            wlan.update(wlan_options)

        data: Dict[str, Any] = {
            "type": network_type,
            "name": name,
            "wlan": wlan,
        }

        if description:
            data["description"] = description

        data.update(kwargs)

        return self.client.post("/wifiNetworks", data=data)
    
    def update(self, wlan_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing WLAN.
        
        Args:
            wlan_id: ID of the WLAN to update
            **kwargs: WLAN properties to update
            
        Returns:
            Dict containing the updated WLAN details
            
        Raises:
            ResourceNotFoundError: If the WLAN does not exist
        """
        try:
            return self.client.put(f"/wifiNetworks/{wlan_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"WLAN with ID {wlan_id} not found")
    
    def delete(self, wlan_id: str) -> None:
        """
        Delete a WLAN.
        
        Args:
            wlan_id: ID of the WLAN to delete
            
        Raises:
            ResourceNotFoundError: If the WLAN does not exist
        """
        try:
            self.client.delete(f"/wifiNetworks/{wlan_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"WLAN with ID {wlan_id} not found")
    
    def list_venue_wlans(self,
                        venue_id: str,
                        search_string: Optional[str] = None,
                        page_size: int = 100,
                        page: int = 0,
                        **kwargs) -> Dict[str, Any]:
        """
        List WLANs deployed in a venue.

        Args:
            venue_id: ID of the venue
            search_string: Optional search string to filter WLANs
            page_size: Number of results per page
            page: Page number to retrieve
            **kwargs: Additional filter parameters

        Returns:
            Dict containing WLANs deployed in the venue

        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        data = {
            "pageSize": page_size,
            "page": page
        }

        if search_string:
            data["searchString"] = search_string

        # Add venue filter
        data["filters"] = data.get("filters", {})
        data["filters"]["venueId"] = venue_id

        # Add any additional filters
        for key, value in kwargs.items():
            if key != "filters":
                data["filters"] = data.get("filters", {})
                data["filters"][key] = value
            else:
                # If filters is explicitly provided
                data["filters"] = {**data.get("filters", {}), **value}

        try:
            return self.client.post("/venues/wifiNetworks/query", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def deploy_to_venue(self,
                      wlan_id: str,
                      venue_id: str,
                      is_all_ap_groups: bool = True,
                      **kwargs) -> Dict[str, Any]:
        """
        Deploy a WLAN to a venue.

        Args:
            wlan_id: ID of the WLAN to deploy
            venue_id: ID of the venue to deploy to
            is_all_ap_groups: Whether to deploy to all AP groups (default True)
            **kwargs: Additional deployment parameters

        Returns:
            Dict containing the deployment details

        Raises:
            ResourceNotFoundError: If the WLAN or venue does not exist
        """
        data: Dict[str, Any] = {
            "isAllApGroups": is_all_ap_groups,
        }
        data.update(kwargs)

        try:
            return self.client.put(
                f"/venues/{venue_id}/wifiNetworks/{wlan_id}", data=data
            )
        except ResourceNotFoundError as e:
            if "network" in str(e).lower() or "wlan" in str(e).lower():
                raise ResourceNotFoundError(message=f"WLAN with ID {wlan_id} not found")
            else:
                raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def undeploy_from_venue(self, wlan_id: str, venue_id: str) -> None:
        """
        Remove a WLAN deployment from a venue.

        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue

        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        try:
            self.client.delete(f"/venues/{venue_id}/wifiNetworks/{wlan_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )
    
    def get_venue_wlan_settings(self, wlan_id: str, venue_id: str) -> Dict[str, Any]:
        """
        Get WLAN deployment settings in a venue.

        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue

        Returns:
            Dict containing the deployment settings

        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        try:
            return self.client.get(
                f"/venues/{venue_id}/wifiNetworks/{wlan_id}/settings"
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )
    
    def update_venue_wlan_settings(self,
                                 wlan_id: str,
                                 venue_id: str,
                                 **kwargs) -> Dict[str, Any]:
        """
        Update WLAN deployment settings in a venue.

        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue
            **kwargs: Settings to update

        Returns:
            Dict containing the updated deployment settings

        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/wifiNetworks/{wlan_id}/settings",
                data=kwargs,
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )

    def get_radius_proxy_settings(self, wlan_id: str) -> Dict[str, Any]:
        """
        Get RADIUS server profile settings for a WiFi network.

        Returns proxy mode flags (enableAuthProxy, enableAccountingProxy)
        and related RADIUS configuration.

        Args:
            wlan_id: ID of the WiFi network

        Returns:
            Dict containing the RADIUS proxy settings
        """
        return self.client.get(f"/wifiNetworks/{wlan_id}/radiusServerProfileSettings")

    def associate_dpsk_service(self, wlan_id: str, dpsk_service_id: str) -> Dict[str, Any]:
        """
        Associate a DPSK service with a WiFi network.

        Args:
            wlan_id: The WiFi network ID
            dpsk_service_id: The DPSK service ID

        Returns:
            Association response
        """
        path = f"/wifiNetworks/{wlan_id}/dpskServices/{dpsk_service_id}"

        logger.debug(f"Associating DPSK service {dpsk_service_id} with WiFi network {wlan_id}")
        return self.client.put(path, {})