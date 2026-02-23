"""
RUCKUS One (R1) Python SDK

A Python SDK for interacting with the RUCKUS One (R1) network management system API.
"""

__version__ = "0.1.0"

# Export the RuckusOneClient class for direct import
from .client import RuckusOneClient

# Import modules to make them available when the client is created
from .modules.venues import Venues
from .modules.access_points import AccessPoints
from .modules.switches import Switches
from .modules.wlans import WLANs
from .modules.vlans import VLANs