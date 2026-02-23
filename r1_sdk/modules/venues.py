"""
Venues module for the RUCKUS One API.

This module handles venue management operations such as creating, retrieving,
updating, and deleting venues.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class Venues:
    """
    Venues API module.
    
    Handles operations related to venues in the RUCKUS One API.
    """
    
    def __init__(self, client):
        """
        Initialize the Venues module.
        
        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.venues = self
    
    def list(self, 
             search_string: Optional[str] = None, 
             page_size: int = 100, 
             page: int = 0, 
             sort_field: Optional[str] = None, 
             sort_order: str = "ASC",
             data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List venues with optional filtering.
        
        Args:
            search_string: Optional search string to filter venues
            page_size: Number of results per page
            page: Page number to retrieve
            sort_field: Field to sort by
            sort_order: Sort order ("ASC" or "DESC") - must be uppercase
            data: Optional direct data dictionary (overrides other parameters if provided)
            
        Returns:
            Dict containing venues and pagination information
        """
        # If direct data dictionary is provided, use it (for backward compatibility)
        if data is not None:
            query_data = data
        else:
            # Otherwise, build the data dictionary from the parameters
            query_data = {
                "pageSize": page_size,
                "page": page,
                "sortOrder": sort_order.upper()  # API requires uppercase sort order
            }
            
            if search_string:
                query_data["searchString"] = search_string
                
            if sort_field:
                query_data["sortField"] = sort_field
        
        logger.debug(f"Listing venues with parameters: {query_data}")
        try:
            result = self.client.post("/venues/query", data=query_data)
            logger.debug(f"List venues response keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error listing venues: {str(e)}")
            raise
    
    def get(self, venue_id: str) -> Dict[str, Any]:
        """
        Retrieve a venue by ID.
        
        Args:
            venue_id: ID of the venue to retrieve
            
        Returns:
            Dict containing venue details
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        try:
            return self.client.get(f"/venues/{venue_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def create(self, 
               name: str, 
               address: Dict[str, Any], 
               description: Optional[str] = None, 
               timezone: Optional[str] = None,
               **kwargs) -> Dict[str, Any]:
        """
        Create a new venue.
        
        Args:
            name: Name of the venue
            address: Address information (street, city, state, etc.)
            description: Optional description of the venue
            timezone: Optional timezone for the venue
            **kwargs: Additional venue properties
            
        Returns:
            Dict containing the created venue details
        """
        data = {
            "name": name,
            "address": address
        }
        
        if description:
            data["description"] = description
            
        if timezone:
            data["timezone"] = timezone
            
        # Add any additional properties
        data.update(kwargs)
        
        return self.client.post("/venues", data=data)
    
    def update(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing venue.
        
        Args:
            venue_id: ID of the venue to update
            **kwargs: Venue properties to update
            
        Returns:
            Dict containing the updated venue details
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        try:
            return self.client.put(f"/venues/{venue_id}", data=kwargs)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def delete(self, venue_id: str) -> None:
        """
        Delete a venue.
        
        Args:
            venue_id: ID of the venue to delete
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        try:
            self.client.delete(f"/venues/{venue_id}")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def get_aps(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get access points for a venue.
        
        Args:
            venue_id: ID of the venue
            **kwargs: Additional filtering parameters
            
        Returns:
            Dict containing access points in the venue
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        params = kwargs
        
        try:
            logger.debug(f"Getting APs for venue {venue_id} with params: {params}")
            return self.client.get(f"/venues/{venue_id}/aps")
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def get_switches(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get switches for a venue.
        
        Args:
            venue_id: ID of the venue
            **kwargs: Additional filtering parameters
            
        Returns:
            Dict containing switches in the venue
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        data = kwargs
        
        try:
            return self.client.post(f"/venues/{venue_id}/switches/query", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
            
    def get_wlans(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get WLANs for a venue.
        
        Args:
            venue_id: ID of the venue
            **kwargs: Additional filtering parameters
            
        Returns:
            Dict containing WLANs in the venue
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        data = kwargs
        
        try:
            return self.client.post(f"/venues/{venue_id}/wifiNetworks/query", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")
    
    def get_clients(self, venue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get clients for a venue.
        
        Args:
            venue_id: ID of the venue
            **kwargs: Additional filtering parameters
            
        Returns:
            Dict containing clients in the venue
            
        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        data = kwargs
        
        try:
            return self.client.post(f"/venues/{venue_id}/clients/query", data=data)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(message=f"Venue with ID {venue_id} not found")