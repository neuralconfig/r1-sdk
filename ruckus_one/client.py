"""
Client module for the RUCKUS One (R1) API.

This module provides the main API client for interacting with the RUCKUS One API.
"""

import json
import logging
import requests
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from .auth import Auth, RUCKUS_REGIONS

logger = logging.getLogger(__name__)

from .exceptions import (
    APIError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError
)


logger = logging.getLogger(__name__)


class RuckusOneClient:
    """
    Main client for interacting with the RUCKUS One API.
    
    Provides methods for making requests to the API and handling responses.
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        region: str = "na",
        auth: Optional[Auth] = None
    ):
        """
        Initialize the RuckusOneClient.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tenant_id: RUCKUS One tenant ID
            region: API region (na, eu, asia)
            auth: Pre-configured Auth instance
        
        Raises:
            ValueError: If authentication parameters are missing
        """
        if auth:
            self.auth = auth
        elif client_id and client_secret and tenant_id:
            self.auth = Auth(client_id, client_secret, tenant_id, region)
        else:
            raise ValueError("Either auth or client_id/client_secret/tenant_id must be provided")
            
        self.base_url = f"https://{RUCKUS_REGIONS.get(region, RUCKUS_REGIONS['na'])}"
        self.tenant_id = tenant_id
        
        # Initialize placeholder for resource modules
        self.venues = None
        self.aps = None
        self.switches = None
        self.wlans = None
        self.vlans = None
        self.clients = None
        self.dpsk = None
        self.identity_groups = None
        self.identities = None
        
        # Automatically initialize the modules
        self._init_modules()
        
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        raw_response: bool = False
    ) -> Any:
        """
        Make a request to the RUCKUS One API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Custom headers
            raw_response: If True, return the raw response object
        
        Returns:
            API response data, or raw response if raw_response=True
        
        Raises:
            APIError: If the API returns an error
            AuthenticationError: If authentication fails
        """
        # Build the request URL
        url = urljoin(self.base_url, path.lstrip('/'))
        
        logger.debug(f"Making {method} request to {url}")
        
        # Get authentication headers
        request_headers = self.auth.get_auth_headers()
        logger.debug(f"Using auth headers: {request_headers}")
            
        # Add custom headers
        if headers:
            request_headers.update(headers)
            logger.debug(f"Added custom headers: {headers}")
        
        # Log request body for debugging
        if json_data:
            logger.debug(f"Request JSON data: {json_data}")
        if data:
            logger.debug(f"Request form data: {data}")
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            # Log response content for debugging (be careful with sensitive data)
            if response.content:
                try:
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type or 'json' in content_type:
                        logger.debug(f"Response JSON: {response.json()}")
                    else:
                        logger.debug(f"Response content length: {len(response.content)} bytes")
                except Exception as e:
                    logger.debug(f"Could not parse response content: {e}")
            
            # Handle response status
            if 200 <= response.status_code < 300:
                if raw_response:
                    return response
                
                # Return response data if successful
                content_type = response.headers.get('Content-Type', '')
                # Check for JSON content types (including vendor-specific ones)
                if response.content and ('application/json' in content_type or 'json' in content_type):
                    return response.json()
                return response.content
            
            # Handle error responses
            logger.error(f"Request failed with status code {response.status_code}: {response.text}")
            self._handle_error_response(response)
            
        except requests.RequestException as e:
            logger.exception(f"Request failed: {str(e)}")
            raise APIError(message=f"Request failed: {str(e)}")
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: Response object
        
        Raises:
            AuthenticationError: For authentication errors
            ResourceNotFoundError: When a resource is not found
            ValidationError: For validation errors
            RateLimitError: When rate limits are exceeded
            ServerError: For server-side errors
            APIError: For other API errors
        """
        error_detail = None
        
        # Try to parse error details from response
        try:
            content_type = response.headers.get('Content-Type', '')
            if response.content and ('application/json' in content_type or 'json' in content_type):
                error_data = response.json()
                error_detail = error_data.get('message') or error_data.get('error') or error_data
        except ValueError:
            error_detail = response.text
        
        status_code = response.status_code
        
        # Map status codes to appropriate exceptions
        if status_code == 401:
            raise AuthenticationError(f"Authentication failed: {error_detail}")
        elif status_code == 404:
            raise ResourceNotFoundError(detail=error_detail)
        elif status_code == 400:
            raise ValidationError(detail=error_detail)
        elif status_code == 429:
            raise RateLimitError(detail=error_detail)
        elif 500 <= status_code < 600:
            raise ServerError(status_code=status_code, detail=error_detail)
        else:
            raise APIError(
                status_code=status_code,
                detail=error_detail,
                message=f"API error occurred: {error_detail}"
            )
    
    def get(self, path: str, **kwargs) -> Any:
        """
        Make a GET request to the API.
        
        Args:
            path: API endpoint path
            **kwargs: Additional arguments to pass to request()
        
        Returns:
            API response data
        """
        return self.request('GET', path, **kwargs)
    
    def post(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a POST request to the API.
        
        Args:
            path: API endpoint path
            data: JSON data
            **kwargs: Additional arguments to pass to request()
        
        Returns:
            API response data
        """
        return self.request('POST', path, json_data=data, **kwargs)
    
    def put(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a PUT request to the API.
        
        Args:
            path: API endpoint path
            data: JSON data
            **kwargs: Additional arguments to pass to request()
        
        Returns:
            API response data
        """
        return self.request('PUT', path, json_data=data, **kwargs)
    
    def patch(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a PATCH request to the API.
        
        Args:
            path: API endpoint path
            data: JSON data
            **kwargs: Additional arguments to pass to request()
        
        Returns:
            API response data
        """
        return self.request('PATCH', path, json_data=data, **kwargs)
    
    def delete(self, path: str, **kwargs) -> Any:
        """
        Make a DELETE request to the API.
        
        Args:
            path: API endpoint path
            **kwargs: Additional arguments to pass to request()
        
        Returns:
            API response data
        """
        return self.request('DELETE', path, **kwargs)
        
    def _init_modules(self):
        """
        Initialize all API modules.
        
        This method is called during client initialization to ensure
        all module references are properly set up.
        """
        # Import modules here to avoid circular imports
        from .modules.venues import Venues
        from .modules.access_points import AccessPoints
        from .modules.switches import Switches
        from .modules.wlans import WLANs
        from .modules.vlans import VLANs
        from .modules.dpsk import DPSK
        from .modules.identity_groups import IdentityGroups
        from .modules.identities import Identities
        
        # Initialize modules (they will register themselves with the client)
        Venues(self)
        AccessPoints(self) 
        Switches(self)
        WLANs(self)
        VLANs(self)
        DPSK(self)
        IdentityGroups(self)
        Identities(self)
        
        # Log module initialization
        logger.debug("All API modules initialized successfully")