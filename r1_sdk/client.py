"""
Client module for the R1 API.

This module provides the main API client for interacting with the R1 API.
"""

import configparser
import logging
import os
import requests
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from .auth import Auth, RUCKUS_REGIONS
from .exceptions import (
    APIError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError
)

logger = logging.getLogger(__name__)


class R1Client:
    """
    Main client for interacting with the R1 API.

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
        Initialize the R1Client.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tenant_id: R1 tenant ID
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

        # Initialize all API modules
        self._init_modules()

    @classmethod
    def from_config(cls, config_path: str = 'config.ini', section: str = 'credentials') -> 'R1Client':
        """Create client from a config.ini file."""
        config = configparser.ConfigParser()
        config.read(config_path)
        return cls(
            client_id=config[section]['client_id'],
            client_secret=config[section]['client_secret'],
            tenant_id=config[section]['tenant_id'],
            region=config[section].get('region', 'na'),
        )

    @classmethod
    def from_env(cls) -> 'R1Client':
        """Create client from environment variables (R1_CLIENT_ID, R1_CLIENT_SECRET, R1_TENANT_ID, R1_REGION)."""
        return cls(
            client_id=os.environ['R1_CLIENT_ID'],
            client_secret=os.environ['R1_CLIENT_SECRET'],
            tenant_id=os.environ['R1_TENANT_ID'],
            region=os.environ.get('R1_REGION', 'na'),
        )

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
        Make a request to the R1 API.

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
        url = urljoin(self.base_url, path.lstrip('/'))

        logger.debug(f"Making {method} request to {url}")

        # Get authentication headers
        request_headers = self.auth.get_auth_headers()

        # Add custom headers
        if headers:
            request_headers.update(headers)

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

            # Auto-refresh on 401 and retry once
            if response.status_code == 401:
                logger.debug("Received 401, refreshing token and retrying")
                self.auth.refresh_token()
                request_headers = self.auth.get_auth_headers()
                if headers:
                    request_headers.update(headers)
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers
                )
                logger.debug(f"Retry response status: {response.status_code}")

            # Handle response status
            if 200 <= response.status_code < 300:
                if raw_response:
                    return response

                content_type = response.headers.get('Content-Type', '')
                if response.content and ('application/json' in content_type or 'json' in content_type):
                    return response.json()
                return response.content

            # Handle error responses
            logger.error(f"Request failed with status code {response.status_code}")
            self._handle_error_response(response)

        except requests.RequestException as e:
            logger.exception(f"Request failed: {str(e)}")
            raise APIError(message=f"Request failed: {str(e)}")

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        Raises:
            AuthenticationError: For authentication errors
            ResourceNotFoundError: When a resource is not found
            ValidationError: For validation errors
            RateLimitError: When rate limits are exceeded
            ServerError: For server-side errors
            APIError: For other API errors
        """
        error_detail = None

        try:
            content_type = response.headers.get('Content-Type', '')
            if response.content and ('application/json' in content_type or 'json' in content_type):
                error_data = response.json()
                error_detail = error_data.get('message') or error_data.get('error') or error_data
        except ValueError:
            error_detail = response.text

        status_code = response.status_code

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
        """Make a GET request to the API."""
        return self.request('GET', path, **kwargs)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Make a POST request to the API."""
        return self.request('POST', path, json_data=data, **kwargs)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Make a PUT request to the API."""
        return self.request('PUT', path, json_data=data, **kwargs)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Make a PATCH request to the API."""
        return self.request('PATCH', path, json_data=data, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        """Make a DELETE request to the API."""
        return self.request('DELETE', path, **kwargs)

    def paginate_query(self, path: str, query_data: Optional[Dict[str, Any]] = None, page_size: int = 100) -> list:
        """Auto-paginate a POST /query endpoint. Returns list of all items.

        Handles two R1 API pagination formats:
        - Standard: {"data": [...], "totalCount": N, "page": N}
        - Spring-style: {"content": [...], "totalElements": N, "number": N}
        """
        all_data: list = []
        page = 0
        base_query = dict(query_data or {})
        while True:
            q = {**base_query, "pageSize": page_size, "page": page, "sortOrder": "ASC"}
            result = self.post(path, data=q)
            # Handle both response formats
            items = result.get("data") or result.get("content") or []
            all_data.extend(items)
            total = result.get("totalCount") or result.get("totalElements") or result.get("total") or 0
            if len(all_data) >= total or not items:
                break
            page += 1
        return all_data

    def _init_modules(self):
        """Initialize all API modules."""
        from .modules.venues import Venues
        from .modules.aps import APs
        from .modules.switches import Switches
        from .modules.wifi_networks import WiFiNetworks
        from .modules.vlan_pools import VLANPools
        from .modules.dpsk import DPSK
        from .modules.identity_groups import IdentityGroups
        from .modules.identities import Identities
        from .modules.l3_acl_policies import L3AclPolicies
        from .modules.cli_templates import CLITemplates
        from .modules.switch_profiles import SwitchProfiles
        from .modules.radius_server_profiles import RadiusServerProfiles
        from .modules.certificate_templates import CertificateTemplates

        self.venues = Venues(self)
        self.aps = APs(self)
        self.switches = Switches(self)
        self.wifi_networks = WiFiNetworks(self)
        self.vlan_pools = VLANPools(self)
        self.dpsk = DPSK(self)
        self.identity_groups = IdentityGroups(self)
        self.identities = Identities(self)
        self.l3_acl_policies = L3AclPolicies(self)
        self.cli_templates = CLITemplates(self)
        self.switch_profiles = SwitchProfiles(self)
        self.radius_server_profiles = RadiusServerProfiles(self)
        self.certificate_templates = CertificateTemplates(self)

        # Backward compat aliases — remove at 1.0
        self.wlans = self.wifi_networks
        self.vlans = self.vlan_pools
        self.l3acl = self.l3_acl_policies

        logger.debug("All API modules initialized successfully")


# Backward compatibility alias
RuckusOneClient = R1Client
