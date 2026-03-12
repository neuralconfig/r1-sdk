"""
R1 Python SDK

A Python SDK for interacting with the RUCKUS One (R1) network management platform API.
"""

__version__ = "0.5.1"

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
from .modules.aps import APs
from .modules.switches import Switches
from .modules.wifi_networks import WiFiNetworks
from .modules.vlan_pools import VLANPools
from .modules.dpsk import DPSK
from .modules.identities import Identities
from .modules.identity_groups import IdentityGroups
from .modules.l3_acl_policies import L3AclPolicies
from .modules.cli_templates import CLITemplates
from .modules.switch_profiles import SwitchProfiles
from .modules.radius_server_profiles import RadiusServerProfiles
from .modules.certificate_templates import CertificateTemplates
from .modules.mac_registration_pools import MacRegistrationPools
from .modules.policy_sets import PolicySets
from .modules.radius_attribute_groups import RadiusAttributeGroups
from .modules.external_identities import ExternalIdentities
from .modules.policy_templates import PolicyTemplates

# Backward compatibility aliases
from .client import RuckusOneClient
from .exceptions import RuckusOneError

# Backward compat aliases — remove at 1.0
WLANs = WiFiNetworks
VLANs = VLANPools
AccessPoints = APs
L3ACL = L3AclPolicies

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
    "APs",
    "Switches",
    "WiFiNetworks",
    "VLANPools",
    "DPSK",
    "Identities",
    "IdentityGroups",
    "L3AclPolicies",
    "CLITemplates",
    "SwitchProfiles",
    "RadiusServerProfiles",
    "CertificateTemplates",
    "MacRegistrationPools",
    "PolicySets",
    "RadiusAttributeGroups",
    "ExternalIdentities",
    "PolicyTemplates",
    # Backward compat aliases
    "AccessPoints",
    "WLANs",
    "VLANs",
    "L3ACL",
]
