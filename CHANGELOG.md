# Changelog

## [0.2.0] - 2026-02-23

### Breaking Changes
- Package renamed from `ruckus-one` to `neuralconfig-r1-sdk`
- Import path changed from `ruckus_one` to `r1_sdk`
- Main client class renamed from `RuckusOneClient` to `R1Client`
- Base exception renamed from `RuckusOneError` to `R1Error`
- CLI removed (use [r1-tools](https://github.com/neuralconfig/r1-tools) for scripts)
- `cmd2` dependency removed

### Added
- `R1Client.from_config()` factory method — create client from config.ini
- `R1Client.from_env()` factory method — create client from environment variables
- 401 auto-refresh: client retries once on authentication failure
- `py.typed` marker for PEP 561 type checking support
- `pyproject.toml` replacing `setup.py`
- MIT LICENSE file
- Unit test suite (`tests/unit/`)
- OpenAPI spec storage (`openapi-specs/`)
- `__all__` in `r1_sdk/__init__.py` for explicit public API

### Fixed
- Duplicate logger in `client.py`
- Auth token leaked in debug logs (removed sensitive logging)
- Dead `self.clients = None` attribute removed
- Missing exports: DPSK, Identities, IdentityGroups, L3ACL, CLITemplates, SwitchProfiles

### Changed
- Module initialization changed from self-registration to explicit assignment
- All docstrings updated from "RUCKUS One" to "R1"
- Tests reorganized into `tests/unit/` and `tests/integration/`
- README trimmed from 82KB to focused quickstart

### Backward Compatibility
- `RuckusOneClient` available as alias for `R1Client`
- `RuckusOneError` available as alias for `R1Error`

## [0.1.0] - 2024-12-01

### Added
- Initial release
- OAuth2 authentication
- Modules: Venues, AccessPoints, Switches, WLANs, VLANs, DPSK, Identities, IdentityGroups, L3ACL, CLITemplates, SwitchProfiles
