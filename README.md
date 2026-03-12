# R1 Python SDK

A Python SDK for the RUCKUS One (R1) network management platform API.

> **Alpha** — This SDK covers ~12% of the R1 API (183 spec operations across 1,491 in 203 tag groups). 18 modules cover venues, APs, switches, WiFi networks, VLAN pools, DPSK, identities, identity groups, L3 ACL policies, CLI templates, switch profiles, RADIUS server profiles, certificate templates, MAC registration pools, policy sets, RADIUS attribute groups, external identities, and policy templates. 6 modules now have 100% spec coverage. See [API Coverage](#api-coverage) for details.

## Installation

```bash
pip install neuralconfig-r1-sdk
```

Or install from source:

```bash
git clone https://github.com/neuralconfig/r1-sdk.git
cd r1-sdk
pip install -e ".[dev]"
```

## Quick Start

Create a `config.ini`:

```ini
[credentials]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
tenant_id = YOUR_TENANT_ID
region = na
```

```python
from r1_sdk import R1Client

client = R1Client.from_config()

# List venues
venues = client.venues.list()
for venue in venues.get('data', []):
    print(f"{venue['name']} ({venue['id']})")

# List APs
aps = client.aps.list({"pageSize": 100, "page": 0})

# List WiFi networks
networks = client.wifi_networks.list({"pageSize": 100, "page": 0})
```

### Alternative: Environment Variables

```bash
export R1_CLIENT_ID=your_id
export R1_CLIENT_SECRET=your_secret
export R1_TENANT_ID=your_tenant
export R1_REGION=na  # na, eu, asia
```

```python
client = R1Client.from_env()
```

## Documentation

- [Common Patterns](docs/common-patterns.md) — authentication, pagination, error handling, query format
- Per-module API reference in `docs/modules/` (linked from table below)

## API Modules

| Module | Access via | Key Methods |
|--------|-----------|-------------|
| [Venues](docs/modules/venues.md) | `client.venues` | `list()`, `list_all()`, `get()`, `create()`, `update()`, `delete()`, `get_aps()`, `get_switches()`, `get_wlans()`, `get_clients()` |
| [APs](docs/modules/aps.md) | `client.aps` | `list()`, `list_all()`, `get()`, `update()`, `reboot()`, `add_to_venue()`, `remove_from_venue()`, `add_to_group()`, `get_clients()`, `get_radio_settings()`, `update_radio_settings()`, `get_statistics()`, `get_support_logs()`, `get_venue_ap_management_vlan()`, `update_venue_ap_management_vlan()`, `get_ap_management_vlan()`, `update_ap_management_vlan()` |
| [Switches](docs/modules/switches.md) | `client.switches` | `list()`, `list_all()`, `get()`, `update()`, `reboot()`, `add_to_venue()`, `remove_from_venue()`, `get_ports()`, `configure_port()`, `get_vlans()`, `configure_vlan()`, `create_vlan()`, `delete_vlan()`, `get_statistics()` |
| [WiFi Networks](docs/modules/wifi_networks.md) | `client.wifi_networks` | `list()`, `list_all()`, `get()`, `create()`, `update()`, `delete()`, `list_venue_wlans()`, `deploy_to_venue()`, `undeploy_from_venue()`, `get_venue_wlan_settings()`, `update_venue_wlan_settings()`, `get_radius_proxy_settings()`, `associate_dpsk_service()`, `activate_mac_pool()`, `deactivate_mac_pool()` |
| [VLAN Pools](docs/modules/vlan_pools.md) | `client.vlan_pools` | `list_pools()`, `get_vlan_pool()`, `create_vlan_pool()`, `update_vlan_pool()`, `delete_vlan_pool()`, `list_profiles()`, `get_vlan_pool_profile()`, `create_vlan_pool_profile()`, `update_vlan_pool_profile()`, `delete_vlan_pool_profile()` |
| [DPSK](docs/modules/dpsk.md) | `client.dpsk` | `list_services()`, `get_service()`, `create_service()`, `update_service()`, `delete_service()`, `list_passphrases()`, `list_all_passphrases()`, `get_passphrase()`, `create_passphrases()`, `update_passphrase()`, `patch_passphrase()`, `delete_passphrases()`, `batch_update_passphrases()`, `list_devices()`, `query_devices()`, `add_devices()`, `update_devices()`, `remove_devices()`, `import_passphrases_csv()`, `export_passphrases_csv()` |
| [Identities](docs/modules/identities.md) | `client.identities` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `bulk_delete()`, `get_devices()`, `add_device()`, `remove_device()`, `update_ethernet_ports()`, `delete_ethernet_port()`, `retry_vni_allocation()`, `import_csv()`, `export_csv()` |
| [Identity Groups](docs/modules/identity_groups.md) | `client.identity_groups` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `associate_dpsk_pool()`, `associate_policy_set()`, `remove_policy_set()`, `associate_mac_pool()`, `export_csv()` |
| [L3 ACL Policies](docs/modules/l3_acl_policies.md) | `client.l3_acl_policies` | `list()`, `get()`, `create()`, `update()`, `delete()`, `create_rule()` |
| [CLI Templates](docs/modules/cli_templates.md) | `client.cli_templates` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `bulk_delete()`, `get_examples()`, `associate_with_venue()`, `disassociate_from_venue()`, `get_variables()`, `add_variable()`, `update_variable()`, `delete_variable()`, `get_venue_switches()`, `add_venue_switches()`, `remove_venue_switches()` |
| [Switch Profiles](docs/modules/switch_profiles.md) | `client.switch_profiles` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `bulk_delete()`, `associate_with_venue()`, `disassociate_from_venue()`, `get_venue_profiles()`, ACL CRUD, VLAN CRUD, trusted port CRUD, CLI variable methods, switch mapping methods |
| [RADIUS Server Profiles](docs/modules/radius_server_profiles.md) | `client.radius_server_profiles` | `list()`, `query()`, `get()`, `get_for_wifi_network()` |
| [Certificate Templates](docs/modules/certificate_templates.md) | `client.certificate_templates` | `query()`, `get()`, `get_for_wifi_network()` |
| [MAC Registration Pools](docs/modules/mac_registration_pools.md) | `client.mac_registration_pools` | `query()`, `list_all()`, `get()`, `create()`, `create_standalone()`, `update()`, `delete()`, `query_registrations()`, `list_all_registrations()`, `get_registration()`, `create_registration()`, `update_registration()`, `delete_registration()`, `delete_registrations()`, `import_csv()`, `associate_policy_set()`, `remove_policy_set()` |
| [Policy Sets](docs/modules/policy_sets.md) | `client.policy_sets` | `query()`, `list_all()`, `get()`, `create()`, `update()`, `delete()`, `list_policies()`, `add_policy()`, `remove_policy()`, `get_assignments()` |
| [RADIUS Attribute Groups](docs/modules/radius_attribute_groups.md) | `client.radius_attribute_groups` | `query()`, `list_all()`, `get()`, `create()`, `update()`, `delete()`, `list_attributes()`, `list_vendors()` |
| [External Identities](docs/modules/external_identities.md) | `client.external_identities` | `query()`, `list_all()` |
| [Policy Templates](docs/modules/policy_templates.md) | `client.policy_templates` | `query_templates()`, `list_all_templates()`, `get_template()`, `list_template_attributes()`, `query_policies()`, `list_all_policies()`, `get_policy()`, `create_policy()`, `update_policy()`, `delete_policy()` |

## API Coverage

The R1 API has **1,491 operations** across **203 tag groups**. The SDK covers **183 spec operations (~12%)** with full or partial coverage of 20 tag groups. 6 modules now have 100% spec coverage:

| Tag Group | Spec Ops | SDK Ops | Coverage | SDK Module |
|-----------|----------|---------|----------|------------|
| CLI Templates | 10 | 10 | 100% | `CLITemplates` |
| Switch Profiles | 10 | 10 | 100% | `SwitchProfiles` |
| DPSK Passphrases | 14 | 14 | 100% | `DPSK` |
| Identity Groups | 11 | 11 | 100% | `IdentityGroups` |
| MAC Registration | 19 | 19 | 100% | `MacRegistrationPools` |
| Identities | 15 | 15 | 100% | `Identities` |
| Adaptive Policy Mgmt | 15 | 9 | 60% | `PolicySets`, `PolicyTemplates` |
| Venues | 7 | 4 | 57% | `Venues` |
| VLAN Pools | 17 | 9 | 53% | `VLANPools` |
| Radius Attribute Group | 14 | 7 | 50% | `RadiusAttributeGroups` |
| WiFi Networks | 24 | 11 | 46% | `WiFiNetworks` |
| DPSK Services | 11 | 5 | 45% | `DPSK` |
| Policy Templates | 19 | 8 | 42% | `PolicyTemplates` |
| L3 ACL Policies | 10 | 4 | 40% | `L3AclPolicies` |
| RADIUS Profile | 12 | 3 | 25% | `RadiusServerProfiles` |
| Switch VLANs | 19 | 4 | 21% | `Switches` |
| Switches | 20 | 4 | 20% | `Switches` |
| External Auth Service | 10 | 1 | 10% | `ExternalIdentities` |
| Certificate Template | 21 | 2 | 10% | `CertificateTemplates` |
| APs | 106 | 9 | 8% | `APs` |
| 183 other groups | 1,107 | 0 | 0% | — |

> **Note:** Some query endpoints (e.g. `POST /l3AclPolicies/query`) are tagged under "View" tags in the spec rather than their resource tag. These are counted in the SDK coverage where implemented. See [docs/non-spec-endpoints.md](docs/non-spec-endpoints.md) for SDK methods calling endpoints not in the current spec.

## Error Handling

```python
from r1_sdk import R1Client
from r1_sdk.exceptions import (
    R1Error,              # Base exception
    AuthenticationError,  # 401
    ResourceNotFoundError,  # 404
    ValidationError,      # 400
    RateLimitError,       # 429
    ServerError,          # 5xx
    APIError,             # Other HTTP errors
)

try:
    client.venues.get("nonexistent-id")
except ResourceNotFoundError:
    print("Venue not found")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

The client automatically retries once on 401 (token refresh).

## Development

```bash
git clone https://github.com/neuralconfig/r1-sdk.git
cd r1-sdk
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Run unit tests
.venv/bin/pytest tests/unit/ -v

# Run with coverage
.venv/bin/pytest tests/unit/ --cov=r1_sdk --cov-report=term-missing
```

## License

MIT — see [LICENSE](LICENSE).
