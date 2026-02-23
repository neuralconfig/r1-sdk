"""
DPSK (Dynamic Pre-Shared Key) management module for the RUCKUS One API.

This module provides functionality for managing DPSK services, passphrases,
and device associations.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DPSK:
    """
    DPSK management for the RUCKUS One API.
    
    Provides methods for managing DPSK services, passphrases, and device associations.
    """
    
    def __init__(self, client):
        """
        Initialize the DPSK module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        client.dpsk = self
        
    def list_services(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List DPSK services with optional filtering.
        
        Args:
            filters: Optional filters for the query
            
        Returns:
            List of DPSK services
        """
        # Always use query endpoint (GET is deprecated)
        path = "/dpskServices/query"
        
        # Start with empty query object
        data = {}
        
        # Only add fields that are explicitly provided
        if filters:
            for key in ['page', 'pageSize', 'sortOrder', 'sortField', 'searchString', 
                       'searchTargetFields', 'fields', 'filters']:
                if key in filters and filters[key] is not None:
                    data[key] = filters[key]
        
        logger.debug(f"Listing DPSK services with query: {data}")
        
        try:
            response = self.client.post(path, data)
            
            # Handle different response formats
            if isinstance(response, dict):
                return response.get('data', [])
            elif isinstance(response, list):
                return response
            else:
                logger.error(f"Unexpected response type: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing DPSK services: {e}")
            raise
        
    def get_service(self, pool_id: str) -> Dict[str, Any]:
        """
        Get a specific DPSK service/pool by ID.
        
        Args:
            pool_id: The DPSK pool ID
            
        Returns:
            DPSK service details
        """
        path = f"/dpskServices/{pool_id}"
        
        logger.debug(f"Getting DPSK service: {pool_id}")
        return self.client.get(path)
        
    def create_service(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new DPSK service/pool.
        
        Args:
            name: Name of the DPSK service
            **kwargs: Additional service configuration
            
        Returns:
            Created DPSK service details
        """
        path = "/dpskServices"
        
        data = {
            "name": name,
            **kwargs
        }
        
        logger.debug(f"Creating DPSK service: {data}")
        return self.client.post(path, data)
        
    def update_service(self, pool_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing DPSK service/pool.
        
        Args:
            pool_id: The DPSK pool ID
            updates: Fields to update
            
        Returns:
            Updated DPSK service details
        """
        path = f"/dpskServices/{pool_id}"
        
        logger.debug(f"Updating DPSK service {pool_id}: {updates}")
        return self.client.put(path, updates)
        
    def delete_service(self, pool_id: str) -> None:
        """
        Delete a DPSK service/pool.
        
        Args:
            pool_id: The DPSK pool ID
        """
        path = f"/dpskServices/{pool_id}"
        
        logger.debug(f"Deleting DPSK service: {pool_id}")
        self.client.delete(path)
        
    # Passphrase Management
    
    def list_passphrases(self, pool_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List passphrases in a DPSK pool.
        
        Args:
            pool_id: The DPSK pool ID
            filters: Optional filters for the query
            
        Returns:
            List of passphrases
        """
        # Always use query endpoint (GET is deprecated)
        path = f"/dpskServices/{pool_id}/passphrases/query"
        
        # Start with empty query object
        data = {}
        
        # Only add fields that are explicitly provided
        if filters:
            for key in ['page', 'pageSize', 'sortOrder', 'sortField', 'searchString', 
                       'searchTargetFields', 'fields', 'filters']:
                if key in filters and filters[key] is not None:
                    data[key] = filters[key]
        
        logger.debug(f"Listing passphrases for pool {pool_id} with query: {data}")
        
        try:
            response = self.client.post(path, data)
            
            # Handle different response formats
            if isinstance(response, dict):
                return response.get('data', [])
            elif isinstance(response, list):
                return response
            else:
                logger.error(f"Unexpected response type: {type(response)}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing passphrases: {e}")
            raise
        
    def get_passphrase(self, pool_id: str, passphrase_id: str) -> Dict[str, Any]:
        """
        Get a specific passphrase by ID.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            
        Returns:
            Passphrase details
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}"
        
        logger.debug(f"Getting passphrase {passphrase_id} from pool {pool_id}")
        return self.client.get(path)
        
    def create_passphrases(self, pool_id: str, passphrases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create new passphrases in a DPSK pool.
        
        Args:
            pool_id: The DPSK pool ID
            passphrases: List of passphrase configurations
            
        Returns:
            Creation response with passphrase details
        """
        path = f"/dpskServices/{pool_id}/passphrases"
        
        data = {
            "passphrases": passphrases
        }
        
        logger.debug(f"Creating {len(passphrases)} passphrases in pool {pool_id}")
        return self.client.post(path, data)
        
    def update_passphrase(self, pool_id: str, passphrase_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing passphrase.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            updates: Fields to update
            
        Returns:
            Updated passphrase details
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}"
        
        logger.debug(f"Updating passphrase {passphrase_id} in pool {pool_id}: {updates}")
        return self.client.put(path, updates)
        
    def delete_passphrases(self, pool_id: str, passphrase_ids: List[str]) -> None:
        """
        Delete passphrases from a DPSK pool.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_ids: List of passphrase IDs to delete
        """
        path = f"/dpskServices/{pool_id}/passphrases"
        
        data = {
            "passphraseIds": passphrase_ids
        }
        
        logger.debug(f"Deleting {len(passphrase_ids)} passphrases from pool {pool_id}")
        self.client.delete(path, json_data=data)
        
    def batch_update_passphrases(self, pool_id: str, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch update multiple passphrases.
        
        Args:
            pool_id: The DPSK pool ID
            updates: List of passphrase updates
            
        Returns:
            Update response
        """
        path = f"/dpskServices/{pool_id}/passphrases"
        
        data = {
            "passphrases": updates
        }
        
        logger.debug(f"Batch updating {len(updates)} passphrases in pool {pool_id}")
        return self.client.patch(path, data)
        
    # Device Management
    
    def list_devices(self, pool_id: str, passphrase_id: str) -> List[Dict[str, Any]]:
        """
        List devices associated with a passphrase.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            
        Returns:
            List of associated devices
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}/devices"
        
        logger.debug(f"Listing devices for passphrase {passphrase_id} in pool {pool_id}")
        response = self.client.get(path)
        
        # Handle both list and dict responses
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get('devices', response.get('data', []))
        else:
            return []
        
    def add_devices(self, pool_id: str, passphrase_id: str, devices: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Add devices to a passphrase.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            devices: List of device configurations (MAC addresses)
            
        Returns:
            Addition response
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}/devices"
        
        data = {
            "devices": devices
        }
        
        logger.debug(f"Adding {len(devices)} devices to passphrase {passphrase_id}")
        return self.client.post(path, data)
        
    def update_devices(self, pool_id: str, passphrase_id: str, devices: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Update device associations for a passphrase.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            devices: List of device updates
            
        Returns:
            Update response
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}/devices"
        
        data = {
            "devices": devices
        }
        
        logger.debug(f"Updating {len(devices)} device associations for passphrase {passphrase_id}")
        return self.client.patch(path, data)
        
    def remove_devices(self, pool_id: str, passphrase_id: str, device_macs: List[str]) -> None:
        """
        Remove devices from a passphrase.
        
        Args:
            pool_id: The DPSK pool ID
            passphrase_id: The passphrase ID
            device_macs: List of device MAC addresses to remove
        """
        path = f"/dpskServices/{pool_id}/passphrases/{passphrase_id}/devices"
        
        data = {
            "deviceMacs": device_macs
        }
        
        logger.debug(f"Removing {len(device_macs)} devices from passphrase {passphrase_id}")
        self.client.delete(path, json_data=data)
        
    # Import/Export
    
    def import_passphrases_csv(self, pool_id: str, csv_content: str) -> Dict[str, Any]:
        """
        Import passphrases from CSV content.
        
        Args:
            pool_id: The DPSK pool ID
            csv_content: CSV file content
            
        Returns:
            Import response
        """
        path = f"/dpskServices/{pool_id}/passphrases/csvFiles"
        
        headers = {
            'Content-Type': 'text/csv'
        }
        
        logger.debug(f"Importing passphrases from CSV to pool {pool_id}")
        return self.client.post(path, data=csv_content, headers=headers)
        
    def export_passphrases_csv(self, pool_id: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Export passphrases to CSV format.
        
        Args:
            pool_id: The DPSK pool ID
            filters: Optional filters for export
            
        Returns:
            CSV content
        """
        path = f"/dpskServices/{pool_id}/passphrases/query/csvFiles"
        
        # Start with empty query object
        data = {}
        
        # Only add fields that are explicitly provided
        if filters:
            for key in ['page', 'pageSize', 'sortOrder', 'sortField', 'searchString', 
                       'searchTargetFields', 'fields', 'filters']:
                if key in filters and filters[key] is not None:
                    data[key] = filters[key]
        
        logger.debug(f"Exporting passphrases from pool {pool_id} to CSV with query: {data}")
        response = self.client.post(path, data, raw_response=True)
        
        return response.text
        
    # Network Association
    
    def associate_with_wlan(self, wlan_id: str, dpsk_service_id: str) -> Dict[str, Any]:
        """
        Associate a DPSK service with a WiFi network.
        
        Args:
            wlan_id: The WiFi network ID
            dpsk_service_id: The DPSK service ID
            
        Returns:
            Association response
        """
        path = f"/wifiNetworks/{wlan_id}/dpskServices/{dpsk_service_id}"
        
        logger.debug(f"Associating DPSK service {dpsk_service_id} with WLAN {wlan_id}")
        return self.client.put(path, {})