"""
Identity Groups module for the RUCKUS One API.

This module handles identity group management operations such as creating, retrieving,
updating, and deleting identity groups.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class IdentityGroups:
    """
    Identity Groups API module.
    
    Handles operations related to identity groups in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the Identity Groups module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.identity_groups = self
    
    def list(self) -> Dict[str, Any]:
        """
        List all identity groups.
        
        Returns:
            Dict containing identity groups
        """
        logger.debug("Listing all identity groups")
        try:
            result = self.client.get("/identityGroups")
            logger.debug(f"List identity groups response: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error listing identity groups: {str(e)}")
            raise
    
    def query(self, 
              page: int = 0,
              page_size: int = 20,
              certificate_template_id: Optional[str] = None,
              dpsk_pool_id: Optional[str] = None,
              policy_set_id: Optional[str] = None,
              property_id: Optional[str] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Query identity groups with pagination and filtering.
        
        Args:
            page: Page number (0-based)
            page_size: Number of items per page
            certificate_template_id: Filter by certificate template ID
            dpsk_pool_id: Filter by DPSK pool ID
            policy_set_id: Filter by policy set ID
            property_id: Filter by property ID
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing paginated identity groups
        """
        query_data = {
            "page": page,
            "size": page_size
        }
        
        if certificate_template_id:
            query_data["certificateTemplateId"] = certificate_template_id
        if dpsk_pool_id:
            query_data["dpskPoolId"] = dpsk_pool_id
        if policy_set_id:
            query_data["policySetId"] = policy_set_id
        if property_id:
            query_data["propertyId"] = property_id
            
        # Add any additional parameters
        query_data.update(kwargs)
        
        logger.debug(f"Querying identity groups with parameters: {query_data}")
        try:
            result = self.client.post("/identityGroups/query", data=query_data)
            logger.debug(f"Query identity groups response keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying identity groups: {str(e)}")
            raise
    
    def get(self, group_id: str) -> Dict[str, Any]:
        """
        Retrieve an identity group by ID.
        
        Args:
            group_id: ID of the identity group to retrieve
            
        Returns:
            Dict containing identity group details
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
        """
        try:
            return self.client.get(f"/identityGroups/{group_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")
    
    def create(self, 
               name: str,
               description: Optional[str] = None,
               dpsk_pool_id: Optional[str] = None,
               certificate_template_id: Optional[str] = None,
               policy_set_id: Optional[str] = None,
               property_id: Optional[str] = None,
               **kwargs) -> Dict[str, Any]:
        """
        Create a new identity group.
        
        Args:
            name: Name of the identity group
            description: Optional description of the group
            dpsk_pool_id: Optional DPSK pool ID to associate
            certificate_template_id: Optional certificate template ID
            policy_set_id: Optional policy set ID to associate
            property_id: Optional property ID
            **kwargs: Additional group properties
            
        Returns:
            Dict containing the created identity group details
        """
        data = {
            "name": name
        }
        
        if description:
            data["description"] = description
        if dpsk_pool_id:
            data["dpskPoolId"] = dpsk_pool_id
        if certificate_template_id:
            data["certificateTemplateId"] = certificate_template_id
        if policy_set_id:
            data["policySetId"] = policy_set_id
        if property_id:
            data["propertyId"] = property_id
            
        # Add any additional properties
        data.update(kwargs)
        
        logger.debug(f"Creating identity group with data: {data}")
        return self.client.post("/identityGroups", data=data)
    
    def update(self, group_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing identity group.
        
        Args:
            group_id: ID of the identity group to update
            **kwargs: Identity group properties to update
            
        Returns:
            Dict containing the updated identity group details
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
        """
        try:
            # Note: The API might use PUT or PATCH - adjust if needed
            return self.client.put(f"/identityGroups/{group_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")
    
    def delete(self, group_id: str) -> None:
        """
        Delete an identity group.
        
        Args:
            group_id: ID of the identity group to delete
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
        """
        try:
            self.client.delete(f"/identityGroups/{group_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")
    
    def associate_dpsk_pool(self, group_id: str, dpsk_pool_id: str) -> Dict[str, Any]:
        """
        Associate a DPSK pool with an identity group.
        
        Args:
            group_id: ID of the identity group
            dpsk_pool_id: ID of the DPSK pool to associate
            
        Returns:
            Dict containing operation result
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
        """
        try:
            return self.client.put(f"/identityGroups/{group_id}/dpskPools/{dpsk_pool_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")
    
    def associate_policy_set(self, group_id: str, policy_set_id: str) -> Dict[str, Any]:
        """
        Associate a policy set with an identity group.
        
        Args:
            group_id: ID of the identity group
            policy_set_id: ID of the policy set to associate
            
        Returns:
            Dict containing operation result
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
        """
        try:
            return self.client.put(f"/identityGroups/{group_id}/policySets/{policy_set_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")
    
    def get_identity(self, group_id: str, identity_id: str) -> Dict[str, Any]:
        """
        Get a specific identity within an identity group.
        
        Args:
            group_id: ID of the identity group
            identity_id: ID of the identity
            
        Returns:
            Dict containing identity details
            
        Raises:
            ResourceNotFoundError: If the identity group or identity does not exist
        """
        try:
            return self.client.get(f"/identityGroups/{group_id}/identities/{identity_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group {group_id} or identity {identity_id} not found")
    
    def create_identity(self, group_id: str,
                       name: str,
                       email: Optional[str] = None,
                       description: Optional[str] = None,
                       expiration_date: Optional[str] = None,
                       vlan: Optional[int] = None,
                       devices: Optional[List[Dict[str, Any]]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Create a new identity within an identity group.
        
        Args:
            group_id: ID of the identity group
            name: Name of the identity
            email: Optional email address
            description: Optional description
            expiration_date: Optional expiration date (ISO format)
            vlan: Optional VLAN assignment (1-4094)
            devices: Optional list of devices to associate
            **kwargs: Additional identity properties
            
        Returns:
            Dict containing the created identity details
            
        Raises:
            ResourceNotFoundError: If the identity group does not exist
            ValidationError: If the data is invalid
        """
        data = {
            "name": name
        }
        
        if email:
            data["email"] = email
        if description:
            data["description"] = description
        if expiration_date:
            data["expirationDate"] = expiration_date
        if vlan is not None:
            if not 1 <= vlan <= 4094:
                raise ValidationError(detail="VLAN must be between 1 and 4094")
            data["vlan"] = vlan
        if devices:
            data["devices"] = devices
            
        # Add any additional properties
        data.update(kwargs)
        
        logger.debug(f"Creating identity in group {group_id} with data: {data}")
        try:
            return self.client.post(f"/identityGroups/{group_id}/identities", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Identity group with ID {group_id} not found")