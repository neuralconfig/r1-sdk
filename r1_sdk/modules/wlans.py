"""
WLANs module for the RUCKUS One API.

This module handles WLAN (WiFi network) operations such as creating, retrieving,
updating, and deploying wireless networks.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class WLANs:
    """
    WLANs API module.
    
    Handles operations related to wireless networks in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the WLANs module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.wlans = self
    
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
              security_type: str,
              vlan_id: Optional[int] = None,
              hidden: bool = False,
              description: Optional[str] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Create a new WLAN.
        
        Args:
            name: Name of the WLAN
            ssid: SSID (network name) of the WLAN
            security_type: Security type (e.g., "open", "wpa2-psk", "wpa2-enterprise")
            vlan_id: Optional VLAN ID for the WLAN
            hidden: Whether the SSID is hidden
            description: Optional description of the WLAN
            **kwargs: Additional WLAN properties
            
        Returns:
            Dict containing the created WLAN details
        """
        data = {
            "name": name,
            "ssid": ssid,
            "securityType": security_type,
            "hidden": hidden
        }
        
        if vlan_id is not None:
            data["vlanId"] = vlan_id
            
        if description:
            data["description"] = description
            
        # Add any additional properties
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
            return self.client.post("/venues/networks/query", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def deploy_to_venue(self, 
                      wlan_id: str, 
                      venue_id: str,
                      ap_group_id: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Deploy a WLAN to a venue.
        
        Args:
            wlan_id: ID of the WLAN to deploy
            venue_id: ID of the venue to deploy to
            ap_group_id: Optional AP group ID to deploy to specific APs
            **kwargs: Additional deployment parameters
            
        Returns:
            Dict containing the deployment details
            
        Raises:
            ResourceNotFoundError: If the WLAN or venue does not exist
        """
        data = {
            "wifiNetworkId": wlan_id
        }
        
        if ap_group_id:
            data["apGroupId"] = ap_group_id
            
        # Add any additional parameters
        data.update(kwargs)
        
        try:
            return self.client.post(f"/venues/{venue_id}/networks", data=data)
        except ResourceNotFoundError as e:
            # Check which resource is not found
            if "network" in str(e).lower() or "wlan" in str(e).lower():
                raise ResourceNotFoundError(message=f"WLAN with ID {wlan_id} not found")
            else:
                raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def undeploy_from_venue(self, wlan_id: str, venue_id: str, ap_group_id: Optional[str] = None) -> None:
        """
        Remove a WLAN deployment from a venue.
        
        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue
            ap_group_id: Optional AP group ID if deployed to specific APs
            
        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        url = f"/venues/{venue_id}/networks/{wlan_id}"
        if ap_group_id:
            url += f"?apGroupId={ap_group_id}"
            
        try:
            self.client.delete(url)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )
    
    def get_venue_wlan_settings(self, wlan_id: str, venue_id: str, ap_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get WLAN deployment settings in a venue.
        
        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue
            ap_group_id: Optional AP group ID if deployed to specific APs
            
        Returns:
            Dict containing the deployment settings
            
        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        url = f"/venues/{venue_id}/networks/{wlan_id}"
        if ap_group_id:
            url += f"?apGroupId={ap_group_id}"
            
        try:
            return self.client.get(url)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )
    
    def update_venue_wlan_settings(self, 
                                 wlan_id: str, 
                                 venue_id: str, 
                                 ap_group_id: Optional[str] = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Update WLAN deployment settings in a venue.
        
        Args:
            wlan_id: ID of the WLAN
            venue_id: ID of the venue
            ap_group_id: Optional AP group ID if deployed to specific APs
            **kwargs: Settings to update
            
        Returns:
            Dict containing the updated deployment settings
            
        Raises:
            ResourceNotFoundError: If the WLAN, venue, or deployment does not exist
        """
        url = f"/venues/{venue_id}/networks/{wlan_id}"
        if ap_group_id:
            url += f"?apGroupId={ap_group_id}"
            
        try:
            return self.client.put(url, data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"WLAN with ID {wlan_id} not deployed in venue {venue_id}"
            )