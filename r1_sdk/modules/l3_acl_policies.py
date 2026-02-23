"""
L3 ACL Policies module for the R1 API.

This module handles Layer-3 ACL policy operations such as creating, retrieving, updating, and
deleting L3 ACL policies.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)

# Constants
MAX_L3ACL_RULES = 128


class L3AclPolicies:
    """
    L3 ACL Policies API module.

    Handles operations related to Layer-3 ACL policies in the R1 API.
    """

    def __init__(self, client):
        """
        Initialize the L3AclPolicies module.

        Args:
            client: R1Client instance
        """
        self.client = client
    
    def list(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List L3ACL policies with optional filtering.
        
        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }
            
        Returns:
            Dict containing L3ACL policies and pagination information
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 0,
                "sortOrder": "ASC"
            }
        
        # Make sure sortOrder is uppercase
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()
        
        logger.debug(f"Querying L3ACL policies with data: {query_data}")
            
        try:
            result = self.client.post("/l3AclPolicies/query", data=query_data)
            logger.debug(f"L3ACL policies query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying L3ACL policies: {str(e)}")
            raise
    
    def get(self, l3acl_policy_id: str) -> Dict[str, Any]:
        """
        Retrieve an L3ACL policy by ID.
        
        Args:
            l3acl_policy_id: ID of the L3ACL policy to retrieve
            
        Returns:
            Dict containing L3ACL policy details
            
        Raises:
            ResourceNotFoundError: If the L3ACL policy does not exist
        """
        try:
            return self.client.get(f"/l3AclPolicies/{l3acl_policy_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"L3ACL policy with ID {l3acl_policy_id} not found")
    
    def create(self, 
               name: str, 
               l3_rules: List[Dict[str, Any]],
               description: Optional[str] = None,
               default_access: str = "BLOCK",
               **kwargs) -> Dict[str, Any]:
        """
        Create a new L3ACL policy.
        
        Args:
            name: Name of the L3ACL policy
            l3_rules: List of L3 rule definitions
            description: Optional description of the L3ACL policy
            default_access: Default access policy ("ALLOW" or "BLOCK")
            **kwargs: Additional L3ACL policy properties
            
        Returns:
            Dict containing the creation response (typically with requestId)
            
        Raises:
            ValueError: If the number of rules exceeds the maximum allowed
        """
        # Validate rule count
        if len(l3_rules) > MAX_L3ACL_RULES:
            raise ValueError(f"Too many L3 rules: {len(l3_rules)}. Maximum allowed: {MAX_L3ACL_RULES}")
        
        # Validate rule priorities
        for i, rule in enumerate(l3_rules):
            if 'priority' in rule and rule['priority'] > MAX_L3ACL_RULES:
                raise ValueError(f"Rule {i+1} priority {rule['priority']} exceeds maximum: {MAX_L3ACL_RULES}")
        
        # Build the policy data
        policy_data = {
            "name": name,
            "l3Rules": l3_rules,
            "defaultAccess": default_access.upper()
        }
        
        if description:
            policy_data["description"] = description
            
        # Add any additional properties
        policy_data.update(kwargs)
        
        logger.debug(f"Creating L3ACL policy: {policy_data}")
        
        try:
            return self.client.post("/l3AclPolicies", data=policy_data)
        except Exception as e:
            logger.exception(f"Error creating L3ACL policy: {str(e)}")
            raise
    
    def update(self, 
               l3acl_policy_id: str,
               name: str, 
               l3_rules: List[Dict[str, Any]],
               description: Optional[str] = None,
               default_access: str = "BLOCK",
               **kwargs) -> Dict[str, Any]:
        """
        Update an existing L3ACL policy.
        
        Args:
            l3acl_policy_id: ID of the L3ACL policy to update
            name: Name of the L3ACL policy
            l3_rules: List of L3 rule definitions
            description: Optional description of the L3ACL policy
            default_access: Default access policy ("ALLOW" or "BLOCK")
            **kwargs: Additional L3ACL policy properties
            
        Returns:
            Dict containing the update response (typically with requestId)
        """
        # Build the policy data
        policy_data = {
            "name": name,
            "l3Rules": l3_rules,
            "defaultAccess": default_access.upper()
        }
        
        if description:
            policy_data["description"] = description
            
        # Add any additional properties
        policy_data.update(kwargs)
        
        logger.debug(f"Updating L3ACL policy {l3acl_policy_id}: {policy_data}")
        
        try:
            return self.client.put(f"/l3AclPolicies/{l3acl_policy_id}", data=policy_data)
        except Exception as e:
            logger.exception(f"Error updating L3ACL policy: {str(e)}")
            raise
    
    def delete(self, l3acl_policy_id: str) -> Dict[str, Any]:
        """
        Delete an L3ACL policy.
        
        Args:
            l3acl_policy_id: ID of the L3ACL policy to delete
            
        Returns:
            Dict containing the deletion response (typically with requestId)
            
        Raises:
            ResourceNotFoundError: If the L3ACL policy does not exist
        """
        try:
            return self.client.delete(f"/l3AclPolicies/{l3acl_policy_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"L3ACL policy with ID {l3acl_policy_id} not found")
    
    def create_rule(self,
                   description: str,
                   priority: int,
                   access: str = "ALLOW",
                   source_enable_ip_subnet: bool = False,
                   source_ip: Optional[str] = None,
                   source_ip_mask: Optional[str] = None,
                   destination_enable_ip_subnet: bool = False,
                   destination_ip: Optional[str] = None,
                   destination_ip_mask: Optional[str] = None,
                   destination_port: Optional[str] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Create an L3 rule dictionary.
        
        Args:
            description: Description of the rule
            priority: Rule priority (lower number = higher priority)
            access: Access type ("ALLOW" or "BLOCK")
            source_enable_ip_subnet: Enable IP subnet for source
            source_ip: Source IP address
            source_ip_mask: Source IP mask
            destination_enable_ip_subnet: Enable IP subnet for destination
            destination_ip: Destination IP address
            destination_ip_mask: Destination IP mask
            destination_port: Destination port
            **kwargs: Additional rule properties
            
        Returns:
            Dict containing the L3 rule definition
        """
        rule = {
            "description": description,
            "priority": priority,
            "access": access.upper(),
            "source": {
                "enableIpSubnet": source_enable_ip_subnet
            },
            "destination": {
                "enableIpSubnet": destination_enable_ip_subnet
            }
        }
        
        if source_enable_ip_subnet and source_ip:
            rule["source"]["ip"] = source_ip
            if source_ip_mask:
                rule["source"]["ipMask"] = source_ip_mask
            
        if destination_enable_ip_subnet and destination_ip:
            rule["destination"]["ip"] = destination_ip
            if destination_ip_mask:
                rule["destination"]["ipMask"] = destination_ip_mask
            
        if destination_port:
            rule["destination"]["port"] = destination_port
            
        # Add any additional properties
        rule.update(kwargs)
        
        return rule