"""Verify all public exports are importable."""

import r1_sdk


def test_version():
    assert r1_sdk.__version__ == "0.4.2"


def test_client_exports():
    from r1_sdk import R1Client, RuckusOneClient
    assert R1Client is RuckusOneClient


def test_exception_exports():
    from r1_sdk import (
        R1Error,
        RuckusOneError,
        AuthenticationError,
        APIError,
        ResourceNotFoundError,
        ValidationError,
        RateLimitError,
        ServerError,
    )
    assert R1Error is RuckusOneError
    assert issubclass(AuthenticationError, R1Error)
    assert issubclass(APIError, R1Error)
    assert issubclass(ResourceNotFoundError, APIError)
    assert issubclass(ValidationError, APIError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(ServerError, APIError)


def test_module_exports():
    from r1_sdk import (
        Venues,
        APs,
        Switches,
        WiFiNetworks,
        VLANPools,
        DPSK,
        Identities,
        IdentityGroups,
        L3AclPolicies,
        CLITemplates,
        SwitchProfiles,
    )
    for cls in [Venues, APs, Switches, WiFiNetworks, VLANPools,
                DPSK, Identities, IdentityGroups, L3AclPolicies, CLITemplates, SwitchProfiles]:
        assert isinstance(cls, type)


def test_backward_compat_aliases():
    from r1_sdk import AccessPoints, WLANs, VLANs, L3ACL
    from r1_sdk import APs, WiFiNetworks, VLANPools, L3AclPolicies
    assert AccessPoints is APs
    assert WLANs is WiFiNetworks
    assert VLANs is VLANPools
    assert L3ACL is L3AclPolicies


def test_all_list():
    """__all__ should contain all public exports."""
    assert hasattr(r1_sdk, '__all__')
    for name in r1_sdk.__all__:
        assert hasattr(r1_sdk, name), f"{name} in __all__ but not importable"
