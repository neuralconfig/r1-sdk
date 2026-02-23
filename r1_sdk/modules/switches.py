"""
Switches module for the R1 API.

This module handles switch operations such as retrieving, configuring, and
monitoring switches.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class Switches:
    """
    Switches API module.

    Handles operations related to switches in the R1 API.
    """

    def __init__(self, client):
        """
        Initialize the Switches module.

        Args:
            client: R1Client instance
        """
        self.client = client
    
    def list(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List switches with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "VENUE",
                            "value": "venue_id_here"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing switches and pagination information
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
        
        logger.debug(f"Querying switches with data: {query_data}")
            
        try:
            result = self.client.post("/venues/switches/query", data=query_data)
            logger.debug(f"Switches query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying switches: {str(e)}")
            raise
    
    def get(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Retrieve a switch by ID.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to retrieve
            
        Returns:
            Dict containing switch details
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/switches/{switch_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def update(self, venue_id: str, switch_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing switch.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to update
            **kwargs: Switch properties to update
            
        Returns:
            Dict containing the updated switch details
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.put(f"/venues/{venue_id}/switches/{switch_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def reboot(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Reboot a switch.
        
        Args:
            venue_id: ID of the venue that contains the switch
            switch_id: ID of the switch to reboot
            
        Returns:
            Dict containing the reboot operation status
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.post(f"/venues/{venue_id}/switches/{switch_id}/reboot")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
    
    def get_ports(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get ports for a switch or switches.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "SWITCH",
                            "value": "switch_id_here"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0
                }
            
        Returns:
            Dict containing switch ports
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 0,
                "sortOrder": "ASC"  # API requires uppercase
            }
        
        # Make sure sortOrder is uppercase if present
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()
        
        logger.debug(f"Querying switch ports with data: {query_data}")
            
        try:
            result = self.client.post("/venues/switches/switchPorts/query", data=query_data)
            logger.debug(f"Switch ports query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying switch ports: {str(e)}")
            raise
    
    def configure_port(self, venue_id: str, switch_id: str, port_id: str, **kwargs) -> Dict[str, Any]:
        """
        Configure a switch port.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            port_id: ID of the port to configure
            **kwargs: Port configuration parameters
            
        Returns:
            Dict containing the updated port configuration
            
        Raises:
            ResourceNotFoundError: If the switch or port does not exist
        """
        try:
            return self.client.put(
                f"/venues/{venue_id}/switches/{switch_id}/ports/{port_id}",
                data=kwargs
            )
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch port with ID {port_id} not found in switch {switch_id}"
            )
    
    def get_vlans(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Get VLANs configured on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            
        Returns:
            Dict containing VLANs configured on the switch
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        logger.debug(f"Getting VLANs for switch {switch_id} in venue {venue_id}")
        try:
            result = self.client.get(f"/venues/{venue_id}/switches/{switch_id}/vlans")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} VLANs")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch with ID {switch_id} not found in venue {venue_id}")
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
        except Exception as e:
            logger.exception(f"Error getting VLANs: {str(e)}")
            raise
    
    def configure_vlan(self, venue_id: str, switch_id: str, vlan_id: int, **kwargs) -> Dict[str, Any]:
        """
        Configure a VLAN on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to configure
            **kwargs: VLAN configuration parameters
                Example: {
                    "name": "Voice VLAN",
                    "igmpSnooping": True
                }
            
        Returns:
            Dict containing the updated VLAN configuration
            
        Raises:
            ResourceNotFoundError: If the switch or VLAN does not exist
        """
        logger.debug(f"Configuring VLAN {vlan_id} on switch {switch_id} with params: {kwargs}")
        try:
            result = self.client.put(
                f"/venues/{venue_id}/switches/{switch_id}/vlans/{vlan_id}",
                data=kwargs
            )
            logger.debug(f"VLAN configuration successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"VLAN with ID {vlan_id} not found in switch {switch_id}")
            raise ResourceNotFoundError(
                message=f"VLAN with ID {vlan_id} not found in switch {switch_id}"
            )
        except Exception as e:
            logger.exception(f"Error configuring VLAN: {str(e)}")
            raise
            
    def create_vlan(self, venue_id: str, switch_id: str, vlan_id: int, **kwargs) -> Dict[str, Any]:
        """
        Create a new VLAN on a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to create (1-4094)
            **kwargs: VLAN configuration parameters
                Example: {
                    "name": "Data VLAN",
                    "igmpSnooping": False
                }
            
        Returns:
            Dict containing the created VLAN configuration
            
        Raises:
            ResourceNotFoundError: If the switch does not exist
            ValidationError: If the VLAN ID is invalid or already exists
        """
        logger.debug(f"Creating VLAN {vlan_id} on switch {switch_id} with params: {kwargs}")
        
        # Prepare the VLAN data
        data = {"id": vlan_id}
        data.update(kwargs)
        
        try:
            result = self.client.post(
                f"/venues/{venue_id}/switches/{switch_id}/vlans",
                data=data
            )
            logger.debug(f"VLAN creation successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch with ID {switch_id} not found in venue {venue_id}")
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )
        except Exception as e:
            logger.exception(f"Error creating VLAN: {str(e)}")
            raise
    
    def delete_vlan(self, venue_id: str, switch_id: str, vlan_id: int) -> None:
        """
        Delete a VLAN from a switch.
        
        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch
            vlan_id: ID of the VLAN to delete
            
        Raises:
            ResourceNotFoundError: If the switch or VLAN does not exist
        """
        logger.debug(f"Deleting VLAN {vlan_id} from switch {switch_id}")
        try:
            self.client.delete(
                f"/venues/{venue_id}/switches/{switch_id}/vlans/{vlan_id}"
            )
            logger.debug(f"VLAN deletion successful")
        except ResourceNotFoundError:
            logger.error(f"VLAN with ID {vlan_id} not found in switch {switch_id}")
            raise ResourceNotFoundError(
                message=f"VLAN with ID {vlan_id} not found in switch {switch_id}"
            )
        except Exception as e:
            logger.exception(f"Error deleting VLAN: {str(e)}")
            raise
    
    def get_statistics(self, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Get statistics for a switch.

        Args:
            venue_id: ID of the venue
            switch_id: ID of the switch

        Returns:
            Dict containing switch statistics

        Raises:
            ResourceNotFoundError: If the switch does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}/switches/{switch_id}/statistics")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(
                message=f"Switch with ID {switch_id} not found in venue {venue_id}"
            )

    def add_to_venue(self, venue_id: str, serial_number: str, name: str,
                     description: Optional[str] = None,
                     enable_stack: bool = False,
                     jumbo_mode: bool = False,
                     igmp_snooping: str = "none",
                     spanning_tree_priority: Optional[int] = None,
                     initial_vlan_id: Optional[int] = None,
                     trust_ports: Optional[List[str]] = None,
                     stack_members: Optional[List[Dict[str, Any]]] = None,
                     rear_module: str = "none",
                     specified_type: str = "ROUTER",
                     use_simple_endpoint: bool = False,
                     **kwargs) -> Dict[str, Any]:
        """
        Add/preprovision a switch to a venue.

        Based on analysis of existing switches and the official Postman collection,
        this method supports both endpoint variations for switch addition.

        Args:
            venue_id: ID of the venue to add the switch to
            serial_number: Serial number of the switch (used as the switch ID)
            name: Name for the switch (REQUIRED)
            description: Optional description for the switch
            enable_stack: Whether to enable stacking (default: False)
            jumbo_mode: Whether to enable jumbo frames (default: False)
            igmp_snooping: IGMP snooping setting (default: "none")
            spanning_tree_priority: Spanning tree priority (optional)
            initial_vlan_id: Initial VLAN ID (optional)
            trust_ports: List of trust port names (optional)
            stack_members: List of stack member configurations (optional)
            rear_module: Rear module configuration (default: "none")
            specified_type: Switch type specification (default: "ROUTER")
            use_simple_endpoint: Use official Postman endpoint POST /switches (default: False)
            **kwargs: Additional switch configuration parameters

        Returns:
            Dict containing the created switch details

        Raises:
            ValidationError: If the switch data is invalid or API returns error
        """
        logger.debug(f"Adding switch {serial_number} to venue {venue_id}")

        if use_simple_endpoint:
            # Use the official Postman collection endpoint and payload structure
            switch_data = {
                "name": name,
                "id": serial_number,
                "venueId": venue_id,
                "stackMembers": stack_members or [],
                "trustPorts": trust_ports or []
            }
            endpoint = "/switches"
        else:
            # Use the documented API endpoint with full payload
            switch_data = {
                "name": name,
                "id": serial_number,  # The API uses 'id' field for serial number
                "venueId": venue_id,
                "enableStack": enable_stack,
                "jumboMode": jumbo_mode,
                "igmpSnooping": igmp_snooping,
                "rearModule": rear_module,
                "specifiedType": specified_type
            }

            # Add optional fields only if they have values
            if description:
                switch_data["description"] = description
            if trust_ports:
                switch_data["trustPorts"] = trust_ports
            if stack_members:
                switch_data["stackMembers"] = stack_members
            if spanning_tree_priority is not None:
                switch_data["spanningTreePriority"] = spanning_tree_priority
            if initial_vlan_id is not None:
                switch_data["initialVlanId"] = initial_vlan_id

            endpoint = f"/venues/{venue_id}/switches"

        # Add any additional parameters
        switch_data.update(kwargs)

        try:
            result = self.client.post(endpoint, data=switch_data)
            logger.debug(f"Switch addition successful: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error adding switch to venue: {str(e)}")
            raise