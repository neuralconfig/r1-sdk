# Changelog

## [0.4.3] - 2026-03-12

### Fixed
- `paginate_query()` now handles both standard (`data`/`totalCount`) and Spring-style (`content`/`totalElements`) pagination response formats
- `Identities.list_all()` uses GET endpoint with `page`/`size` params instead of non-existent POST `/query` endpoint
- `IdentityGroups.update()` uses PATCH instead of PUT (fixes 405 error)

## [0.4.2] - 2026-03-10

### Added
- **RadiusServerProfiles:** New module — `list()`, `query()`, `get()`, `get_for_wifi_network()`
- **CertificateTemplates:** New module — `query()`, `get()`, `get_for_wifi_network()`
- **WiFiNetworks:** `get_radius_proxy_settings()` method
- **APs:** `remove_from_venue()` and `get_support_logs()` methods
- **Switches:** `remove_from_venue()` method

## [0.4.1] - 2026-02-24

### Breaking Changes
- **WiFiNetworks:** `create()` rewritten to use correct API payload structure (nested `wlan` object with `type`, `wlanSecurity`, `passphrase` fields)
- **WiFiNetworks:** `deploy_to_venue()` changed from `POST /venues/{id}/networks` to `PUT /venues/{id}/wifiNetworks/{id}` — signature changed from `(wlan_id, venue_id, ap_group_id)` to `(wlan_id, venue_id, is_all_ap_groups)`
- **WiFiNetworks:** `undeploy_from_venue()`, `get_venue_wlan_settings()`, `update_venue_wlan_settings()` — endpoints updated from `/networks/` to `/wifiNetworks/`, removed `ap_group_id` parameter
- **WiFiNetworks:** `list_venue_wlans()` endpoint changed from `/venues/networks/query` to `/venues/wifiNetworks/query`

### Added
- **WiFiNetworks:** `SECURITY_TYPE_MAP` for mapping friendly security type names (e.g., `"psk"`, `"wpa3-psk"`, `"owe"`) to API values
- **WiFiNetworks:** `create()` now accepts `passphrase`, `enabled`, `wlan_options`, and `advanced_options` parameters
- **APs:** `add_to_venue()` method for preprovisioning APs

### Fixed
- **Switches:** `add_to_venue()` now sends array payload (`[switch_data]`) as required by the API

## [0.3.0] - 2026-02-23

### Breaking Changes
- Module renames to match API structure:
  - `client.wlans` → `client.wifi_networks` (class `WLANs` → `WiFiNetworks`)
  - `client.vlans` → `client.vlan_pools` (class `VLANs` → `VLANPools`)
  - `client.l3acl` → `client.l3_acl_policies` (class `L3ACL` → `L3AclPolicies`)
  - `client.aps` (class `AccessPoints` → `APs`)
- Methods moved to correct modules:
  - `client.vlans.list_pools()` → `client.vlan_pools.list()`
  - `client.vlans.get_pool()` → `client.vlan_pools.get()`
  - `client.vlans.create_pool()` → `client.vlan_pools.create()`

### Added
- `list_all()` auto-pagination for modules with POST `/query` endpoints:
  Venues, APs, Switches, WiFiNetworks, Identities, IdentityGroups, CLITemplates, SwitchProfiles
- `R1Client.paginate_query()` helper for custom pagination
- 825 unit tests with 99% coverage

### Backward Compatibility
- Old attribute names still work: `client.wlans`, `client.vlans`, `client.l3acl`
- Old class names still importable: `WLANs`, `VLANs`, `AccessPoints`, `L3ACL`
- Aliases will be removed at 1.0

### Removed
- Integration tests (replaced by comprehensive unit tests)

## [0.2.0] - 2026-02-23

### Breaking Changes
- Package renamed from `ruckus-one` to `neuralconfig-r1-sdk`
- Import path changed from `ruckus_one` to `r1_sdk`
- Main client class renamed from `RuckusOneClient` to `R1Client`
- Base exception renamed from `RuckusOneError` to `R1Error`
- CLI removed (use [r1-scripts](https://github.com/neuralconfig/r1-scripts) for scripts)
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
