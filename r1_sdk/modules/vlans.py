"""
VLANs module for the RUCKUS One API.

This module handles VLAN operations such as creating, retrieving, updating, and
configuring VLANs and VLAN pools.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class VLANs:
    """
    VLANs API module.
    
    Handles operations related to VLANs and VLAN pools in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the VLANs module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.vlans = self
    
    def list_pools(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List VLAN pools with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing VLAN pools and pagination information
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
        
        logger.debug(f"Querying VLAN pools with data: {query_data}")
            
        try:
            result = self.client.post("/vlanPools/query", data=query_data)
            logger.debug(f"VLAN pools query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying VLAN pools: {str(e)}")
            raise
    
    def get_vlan_pool(self, vlan_pool_id: str) -> Dict[str, Any]:
        """
        Retrieve a VLAN pool by ID.
        
        Args:
            vlan_pool_id: ID of the VLAN pool to retrieve
            
        Returns:
            Dict containing VLAN pool details
            
        Raises:
            ResourceNotFoundError: If the VLAN pool does not exist
        """
        try:
            return self.client.get(f"/vlanPools/{vlan_pool_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool with ID {vlan_pool_id} not found")
    
    def create_vlan_pool(self, 
                        name: str, 
                        vlans: List[Dict[str, Any]],
                        description: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
        """
        Create a new VLAN pool.
        
        Args:
            name: Name of the VLAN pool
            vlans: List of VLAN definitions (each with ID and optional properties)
            description: Optional description of the VLAN pool
            **kwargs: Additional VLAN pool properties
            
        Returns:
            Dict containing the created VLAN pool details
        """
        data = {
            "name": name,
            "vlans": vlans
        }
        
        if description:
            data["description"] = description
            
        # Add any additional properties
        data.update(kwargs)
        
        return self.client.post("/vlanPools", data=data)
    
    def update_vlan_pool(self, vlan_pool_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing VLAN pool.
        
        Args:
            vlan_pool_id: ID of the VLAN pool to update
            **kwargs: VLAN pool properties to update
            
        Returns:
            Dict containing the updated VLAN pool details
            
        Raises:
            ResourceNotFoundError: If the VLAN pool does not exist
        """
        try:
            return self.client.put(f"/vlanPools/{vlan_pool_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool with ID {vlan_pool_id} not found")
    
    def delete_vlan_pool(self, vlan_pool_id: str) -> None:
        """
        Delete a VLAN pool.
        
        Args:
            vlan_pool_id: ID of the VLAN pool to delete
            
        Raises:
            ResourceNotFoundError: If the VLAN pool does not exist
        """
        try:
            self.client.delete(f"/vlanPools/{vlan_pool_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool with ID {vlan_pool_id} not found")
    
    def list_profiles(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List VLAN pool profiles with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing VLAN pool profiles and pagination information
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
        
        logger.debug(f"Querying VLAN pool profiles with data: {query_data}")
            
        try:
            result = self.client.post("/vlanPoolProfiles/query", data=query_data)
            logger.debug(f"VLAN pool profiles query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying VLAN pool profiles: {str(e)}")
            raise
    
    def get_vlan_pool_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Retrieve a VLAN pool profile by ID.
        
        Args:
            profile_id: ID of the VLAN pool profile to retrieve
            
        Returns:
            Dict containing VLAN pool profile details
            
        Raises:
            ResourceNotFoundError: If the VLAN pool profile does not exist
        """
        try:
            return self.client.get(f"/vlanPoolProfiles/{profile_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool profile with ID {profile_id} not found")
    
    def create_vlan_pool_profile(self, 
                                name: str, 
                                vlan_pool_id: str,
                                description: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """
        Create a new VLAN pool profile.
        
        Args:
            name: Name of the VLAN pool profile
            vlan_pool_id: ID of the VLAN pool to associate with this profile
            description: Optional description of the VLAN pool profile
            **kwargs: Additional VLAN pool profile properties
            
        Returns:
            Dict containing the created VLAN pool profile details
        """
        data = {
            "name": name,
            "vlanPoolId": vlan_pool_id
        }
        
        if description:
            data["description"] = description
            
        # Add any additional properties
        data.update(kwargs)
        
        return self.client.post("/vlanPoolProfiles", data=data)
    
    def update_vlan_pool_profile(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing VLAN pool profile.
        
        Args:
            profile_id: ID of the VLAN pool profile to update
            **kwargs: VLAN pool profile properties to update
            
        Returns:
            Dict containing the updated VLAN pool profile details
            
        Raises:
            ResourceNotFoundError: If the VLAN pool profile does not exist
        """
        try:
            return self.client.put(f"/vlanPoolProfiles/{profile_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool profile with ID {profile_id} not found")
    
    def delete_vlan_pool_profile(self, profile_id: str) -> None:
        """
        Delete a VLAN pool profile.
        
        Args:
            profile_id: ID of the VLAN pool profile to delete
            
        Raises:
            ResourceNotFoundError: If the VLAN pool profile does not exist
        """
        try:
            self.client.delete(f"/vlanPoolProfiles/{profile_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"VLAN pool profile with ID {profile_id} not found")
    
    def get_venue_ap_management_vlan(self, venue_id: str) -> Dict[str, Any]:
        """
        Get AP management VLAN settings for a venue.
        
        Args:
            venue_id: ID of the venue
            
        Returns:
            Dict containing AP management VLAN settings
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/apManagementTrafficVlanSettings")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def update_venue_ap_management_vlan(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update AP management VLAN settings for a venue.
        
        Args:
            venue_id: ID of the venue
            **kwargs: VLAN settings to update
            
        Returns:
            Dict containing the updated VLAN settings
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/apManagementTrafficVlanSettings",
                data=kwargs
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def get_ap_management_vlan(self, venue_id: str, ap_serial: str) -> Dict[str, Any]:
        """
        Get AP management VLAN settings for a specific AP.
        
        Args:
            venue_id: ID of the venue
            ap_serial: Serial number of the AP
            
        Returns:
            Dict containing AP management VLAN settings
            
        Raises:
            ResourceNotFoundError: If the venue or AP does not exist
        """
        try:
            return self.client.get(
                f"/venues/{venue_id}/aps/{ap_serial}/managementTrafficVlanSettings"
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {ap_serial} not found in venue {venue_id}"
            )
    
    def update_ap_management_vlan(self, venue_id: str, ap_serial: str, **kwargs) -> Dict[str, Any]:
        """
        Update AP management VLAN settings for a specific AP.
        
        Args:
            venue_id: ID of the venue
            ap_serial: Serial number of the AP
            **kwargs: VLAN settings to update
            
        Returns:
            Dict containing the updated VLAN settings
            
        Raises:
            ResourceNotFoundError: If the venue or AP does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/aps/{ap_serial}/managementTrafficVlanSettings",
                data=kwargs
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"AP with serial number {ap_serial} not found in venue {venue_id}"
            )