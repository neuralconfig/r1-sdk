"""
R1 Python SDK

A Python SDK for interacting with the RUCKUS One (R1) network management platform API.
"""

__version__ = "0.2.0"

from .client import R1Client
from .exceptions import (
    R1Error,
    AuthenticationError,
    APIError,
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)
from .modules.venues import Venues
from .modules.access_points import AccessPoints
from .modules.switches import Switches
from .modules.wlans import WLANs
from .modules.vlans import VLANs
from .modules.dpsk import DPSK
from .modules.identities import Identities
from .modules.identity_groups import IdentityGroups
from .modules.l3acl import L3ACL
from .modules.cli_templates import CLITemplates
from .modules.switch_profiles import SwitchProfiles

# Backward compatibility aliases
from .client import RuckusOneClient
from .exceptions import RuckusOneError

__all__ = [
    # Client
    "R1Client",
    "RuckusOneClient",
    # Exceptions
    "R1Error",
    "RuckusOneError",
    "AuthenticationError",
    "APIError",
    "ResourceNotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    # Modules
    "Venues",
    "AccessPoints",
    "Switches",
    "WLANs",
    "VLANs",
    "DPSK",
    "Identities",
    "IdentityGroups",
    "L3ACL",
    "CLITemplates",
    "SwitchProfiles",
]
