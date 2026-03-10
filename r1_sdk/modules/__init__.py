"""
R1 API SDK modules.

This package contains the API modules for interacting with different
aspects of the R1 API.
"""

from .venues import Venues
from .aps import APs
from .switches import Switches
from .wifi_networks import WiFiNetworks
from .vlan_pools import VLANPools
from .dpsk import DPSK
from .identity_groups import IdentityGroups
from .identities import Identities
from .l3_acl_policies import L3AclPolicies
from .cli_templates import CLITemplates
from .switch_profiles import SwitchProfiles
from .radius_server_profiles import RadiusServerProfiles
from .certificate_templates import CertificateTemplates

# Backward compat aliases — remove at 1.0
AccessPoints = APs
WLANs = WiFiNetworks
VLANs = VLANPools
L3ACL = L3AclPolicies

__all__ = [
    'Venues',
    'APs',
    'Switches',
    'WiFiNetworks',
    'VLANPools',
    'DPSK',
    'IdentityGroups',
    'Identities',
    'L3AclPolicies',
    'CLITemplates',
    'SwitchProfiles',
    'RadiusServerProfiles',
    'CertificateTemplates',
    # Backward compat aliases
    'AccessPoints',
    'WLANs',
    'VLANs',
    'L3ACL',
]
