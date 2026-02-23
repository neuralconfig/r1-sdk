"""Verify all public exports are importable."""

import r1_sdk


def test_version():
    assert r1_sdk.__version__ == "0.2.0"


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
        AccessPoints,
        Switches,
        WLANs,
        VLANs,
        DPSK,
        Identities,
        IdentityGroups,
        L3ACL,
        CLITemplates,
        SwitchProfiles,
    )
    # All should be classes
    for cls in [Venues, AccessPoints, Switches, WLANs, VLANs,
                DPSK, Identities, IdentityGroups, L3ACL, CLITemplates, SwitchProfiles]:
        assert isinstance(cls, type)


def test_all_list():
    """__all__ should contain all public exports."""
    assert hasattr(r1_sdk, '__all__')
    for name in r1_sdk.__all__:
        assert hasattr(r1_sdk, name), f"{name} in __all__ but not importable"
