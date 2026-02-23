"""
Identities module for the RUCKUS One API.

This module handles identity management operations such as creating, retrieving,
updating, and deleting identities across all identity groups.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class Identities:
    """
    Identities API module.
    
    Handles operations related to identities in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the Identities module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.identities = self
    
    def list(self, 
             page: int = 0,
             page_size: int = 20,
             **kwargs) -> Dict[str, Any]:
        """
        List identities across all identity groups.
        
        Args:
            page: Page number (0-based)
            page_size: Number of items per page
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing paginated identities
        """
        params = {
            "page": page,
            "size": page_size
        }
        params.update(kwargs)
        
        logger.debug(f"Listing identities with parameters: {params}")
        try:
            result = self.client.get("/identities", params=params)
            logger.debug(f"List identities response keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error listing identities: {str(e)}")
            raise
    
    def query(self,
              dpsk_pool_id: Optional[str] = None,
              ethernet_port: Optional[Dict[str, Any]] = None,
              filter_params: Optional[Dict[str, Any]] = None,
              page: int = 0,
              page_size: int = 20,
              sort: Optional[List[str]] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Query identities with advanced filtering and pagination.
        
        Args:
            dpsk_pool_id: Filter by DPSK pool ID
            ethernet_port: Ethernet port filter
            filter_params: Additional filter parameters
            page: Page number (0-based)
            page_size: Number of items per page
            sort: Sort fields
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing filtered identities
        """
        query_data = {
            "page": page,
            "size": page_size
        }
        
        if dpsk_pool_id:
            query_data["dpskPoolId"] = dpsk_pool_id
        if ethernet_port:
            query_data["ethernetPort"] = ethernet_port
        if filter_params:
            query_data["filter"] = filter_params
        if sort:
            query_data["sort"] = sort
            
        # Add any additional parameters
        query_data.update(kwargs)
        
        logger.debug(f"Querying identities with parameters: {query_data}")
        try:
            result = self.client.post("/identities/query", data=query_data)
            logger.debug(f"Query identities response keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying identities: {str(e)}")
            raise
    
    def get(self, group_id: str, identity_id: str) -> Dict[str, Any]:
        """
        Retrieve an identity by ID within a specific group.
        
        Note: The RUCKUS One API requires the group ID to access individual identities.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity to retrieve
            
        Returns:
            Dict containing identity details
            
        Raises:
            ResourceNotFoundError: If the identity or group does not exist
        """
        try:
            return self.client.get(f"/identityGroups/{group_id}/identities/{identity_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} not found")
    
    def update(self, group_id: str, identity_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing identity within a specific group using PATCH.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity to update
            **kwargs: Identity properties to update
            
        Returns:
            Dict containing the updated identity details
            
        Raises:
            ResourceNotFoundError: If the identity or group does not exist
        """
        try:
            return self.client.patch(f"/identityGroups/{group_id}/identities/{identity_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} not found")
    
    def delete(self, group_id: str, identity_id: str) -> None:
        """
        Delete an identity from a specific group.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity to delete
            
        Raises:
            ResourceNotFoundError: If the identity or group does not exist
        """
        try:
            self.client.delete(f"/identityGroups/{group_id}/identities/{identity_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} not found")
    
    def get_devices(self, group_id: str, identity_id: str) -> List[Dict[str, Any]]:
        """
        Get devices associated with an identity.
        
        Note: Based on the identity data structure, devices are included in the identity details.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity
            
        Returns:
            List of devices associated with the identity
            
        Raises:
            ResourceNotFoundError: If the identity or group does not exist
        """
        try:
            identity = self.get(group_id, identity_id)
            return identity.get('devices', [])
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} not found")
    
    def add_device(self, group_id: str,
                   identity_id: str,
                   mac_address: str,
                   name: Optional[str] = None,
                   description: Optional[str] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Add a device to an identity.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity
            mac_address: MAC address of the device (format: XX-XX-XX-XX-XX-XX)
            name: Optional device name
            description: Optional device description
            **kwargs: Additional device properties
            
        Returns:
            Dict containing the operation result
            
        Raises:
            ResourceNotFoundError: If the identity or group does not exist
            ValidationError: If the MAC address format is invalid
        """
        # Validate MAC address format
        import re
        mac_pattern = r'^([0-9A-F]{2}-){5}([0-9A-F]{2})$'
        if not re.match(mac_pattern, mac_address.upper()):
            raise ValidationError(detail="MAC address must be in format XX-XX-XX-XX-XX-XX")
        
        # The API expects an array of devices
        devices = [{
            "macAddress": mac_address.upper()
        }]
        
        if name:
            devices[0]["name"] = name
        if description:
            devices[0]["description"] = description
            
        # Add any additional properties to the device
        devices[0].update(kwargs)
        
        try:
            return self.client.post(f"/identityGroups/{group_id}/identities/{identity_id}/devices", data=devices)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} not found")
    
    def remove_device(self, group_id: str, identity_id: str, mac_address: str) -> None:
        """
        Remove a device from an identity.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity
            mac_address: MAC address of the device to remove
            
        Raises:
            ResourceNotFoundError: If the identity, group, or device does not exist
        """
        try:
            self.client.delete(f"/identityGroups/{group_id}/identities/{identity_id}/devices/{mac_address}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity {identity_id} in group {group_id} or device {mac_address} not found")
    
    def export_csv(self, 
                   dpsk_pool_id: Optional[str] = None,
                   filter_params: Optional[Dict[str, Any]] = None,
                   **kwargs) -> bytes:
        """
        Export identities to CSV format.
        
        Args:
            dpsk_pool_id: Filter by DPSK pool ID
            filter_params: Additional filter parameters
            **kwargs: Additional export parameters
            
        Returns:
            CSV file content as bytes
        """
        data = {}
        
        if dpsk_pool_id:
            data["dpskPoolId"] = dpsk_pool_id
        if filter_params:
            data["filter"] = filter_params
            
        # Add any additional parameters
        data.update(kwargs)
        
        logger.debug(f"Exporting identities to CSV with parameters: {data}")
        return self.client.post("/identities/csvFile", data=data, raw_response=True).content
    
    def import_csv(self, group_id: str, csv_file: bytes) -> Dict[str, Any]:
        """
        Import identities from CSV file into a specific identity group.
        
        Args:
            group_id: ID of the identity group to import into
            csv_file: CSV file content as bytes
            
        Returns:
            Dict containing import results
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
            ValidationError: If the CSV format is invalid
        """
        files = {'file': ('identities.csv', csv_file, 'text/csv')}
        
        try:
            # Note: This endpoint might require multipart/form-data
            return self.client.post(
                f"/identityGroups/{group_id}/identities/csvFile",
                files=files,
                headers={'Content-Type': 'multipart/form-data'}
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")