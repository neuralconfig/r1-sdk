"""
R1 API SDK modules.

This package contains the API modules for interacting with different
aspects of the R1 API.
"""

from .venues import Venues
from .access_points import AccessPoints
from .switches import Switches
from .wlans import WLANs
from .vlans import VLANs
from .dpsk import DPSK
from .identity_groups import IdentityGroups
from .identities import Identities
from .l3acl import L3ACL
from .cli_templates import CLITemplates
from .switch_profiles import SwitchProfiles

__all__ = [
    'Venues',
    'AccessPoints',
    'Switches',
    'WLANs',
    'VLANs',
    'DPSK',
    'IdentityGroups',
    'Identities',
    'L3ACL',
    'CLITemplates',
    'SwitchProfiles',
]
