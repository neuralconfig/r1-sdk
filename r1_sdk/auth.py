"""
Authentication module for the R1 API.

This module handles OAuth2 token generation and management.
"""

import logging
import requests
from typing import Dict, Tuple
from datetime import datetime, timedelta
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# R1 API region endpoints
RUCKUS_REGIONS = {
    "na": "api.ruckus.cloud",
    "eu": "api.eu.ruckus.cloud",
    "asia": "api.asia.ruckus.cloud"
}


class Auth:
    """
    Authentication handler for the R1 API.

    Manages OAuth2 token generation and refreshing for API authentication.
    """

    def __init__(self, client_id: str, client_secret: str, tenant_id: str, region: str = "na"):
        """
        Initialize the Auth handler.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            tenant_id: R1 tenant ID
            region: API region (na, eu, asia)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.region = region
        self.base_url = f"https://{RUCKUS_REGIONS.get(region, RUCKUS_REGIONS['na'])}"
        self._token = None
        self._token_expiry = datetime.now()

    def get_token(self) -> str:
        """
        Get a valid authentication token.

        Returns a cached token if it's still valid, or gets a new one if expired.

        Returns:
            str: JWT authentication token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._token is None or datetime.now() >= self._token_expiry:
            self._token, self._token_expiry = self._authenticate()
        return self._token

    def _authenticate(self) -> Tuple[str, datetime]:
        """
        Authenticate with the R1 API and get a new OAuth2 token.

        Returns:
            Tuple[str, datetime]: JWT token and expiry time

        Raises:
            AuthenticationError: If authentication fails
        """
        token_url = f"{self.base_url}/oauth2/token/{self.tenant_id}"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        logger.debug(f"Authenticating with R1 API at URL: {token_url}")

        try:
            response = requests.post(token_url, data=auth_data)
            logger.debug(f"Auth response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"Auth failed with status {response.status_code}")

            response.raise_for_status()
            data = response.json()

            if 'access_token' not in data:
                raise AuthenticationError("No access token in response")

            # Set token expiry 5 minutes before actual expiry to be safe
            expires_in = data.get('expires_in', 3600)
            expiry_time = datetime.now() + timedelta(seconds=expires_in - 300)

            logger.debug(f"Successfully obtained access token, expires in {expires_in} seconds")
            return data['access_token'], expiry_time

        except requests.RequestException as e:
            logger.exception(f"Authentication request failed: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def refresh_token(self) -> None:
        """
        Force a token refresh.

        Raises:
            AuthenticationError: If refreshing the token fails
        """
        self._token, self._token_expiry = self._authenticate()

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get the authentication headers required for API requests.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token
        """
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }
