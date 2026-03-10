# R1 Python SDK

A Python SDK for the RUCKUS One (R1) network management platform API.

> **Alpha** — This SDK covers ~9% of the R1 API (138 endpoints across 1,491 operations in 203 tag groups). Core modules for venues, APs, switches, WiFi networks, VLAN pools, DPSK, identities, L3 ACL policies, CLI templates, switch profiles, RADIUS server profiles, and certificate templates are implemented. See [API Coverage](#api-coverage) for details.

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
| [WiFi Networks](docs/modules/wifi_networks.md) | `client.wifi_networks` | `list()`, `list_all()`, `get()`, `create()`, `update()`, `delete()`, `list_venue_wlans()`, `deploy_to_venue()`, `undeploy_from_venue()`, `get_venue_wlan_settings()`, `update_venue_wlan_settings()`, `get_radius_proxy_settings()`, `associate_dpsk_service()` |
| [VLAN Pools](docs/modules/vlan_pools.md) | `client.vlan_pools` | `list_pools()`, `get_vlan_pool()`, `create_vlan_pool()`, `update_vlan_pool()`, `delete_vlan_pool()`, `list_profiles()`, `get_vlan_pool_profile()`, `create_vlan_pool_profile()`, `update_vlan_pool_profile()`, `delete_vlan_pool_profile()` |
| [DPSK](docs/modules/dpsk.md) | `client.dpsk` | `list_services()`, `get_service()`, `create_service()`, `update_service()`, `delete_service()`, `list_passphrases()`, `get_passphrase()`, `create_passphrases()`, `update_passphrase()`, `delete_passphrases()`, `batch_update_passphrases()`, `list_devices()`, `add_devices()`, `update_devices()`, `remove_devices()`, `import_passphrases_csv()`, `export_passphrases_csv()` |
| [Identities](docs/modules/identities.md) | `client.identities` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `get_devices()`, `add_device()`, `remove_device()`, `import_csv()`, `export_csv()` |
| [Identity Groups](docs/modules/identity_groups.md) | `client.identity_groups` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `associate_dpsk_pool()`, `associate_policy_set()` |
| [L3 ACL Policies](docs/modules/l3_acl_policies.md) | `client.l3_acl_policies` | `list()`, `get()`, `create()`, `update()`, `delete()`, `create_rule()` |
| [CLI Templates](docs/modules/cli_templates.md) | `client.cli_templates` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `bulk_delete()`, `get_examples()`, `associate_with_venue()`, `disassociate_from_venue()`, `get_variables()`, `add_variable()`, `update_variable()`, `delete_variable()`, `get_venue_switches()`, `add_venue_switches()`, `remove_venue_switches()` |
| [Switch Profiles](docs/modules/switch_profiles.md) | `client.switch_profiles` | `list()`, `list_all()`, `query()`, `get()`, `create()`, `update()`, `delete()`, `bulk_delete()`, `associate_with_venue()`, `disassociate_from_venue()`, `get_venue_profiles()`, ACL CRUD, VLAN CRUD, trusted port CRUD, CLI variable methods, switch mapping methods |
| [RADIUS Server Profiles](docs/modules/radius_server_profiles.md) | `client.radius_server_profiles` | `list()`, `query()`, `get()`, `get_for_wifi_network()` |
| [Certificate Templates](docs/modules/certificate_templates.md) | `client.certificate_templates` | `query()`, `get()`, `get_for_wifi_network()` |

## API Coverage

The R1 API has **1,491 operations** across **203 tag groups**. The SDK covers **138 operations (~9%)** with full or partial coverage of 31 tag groups:

| Tag Group | Spec Ops | SDK Ops | Coverage |
|-----------|----------|---------|----------|
| CLI Templates | 10 | 10 | 100% |
| Switch Profiles | 10 | 10 | 100% |
| DPSK Passphrases | 14 | 12 | 86% |
| Identity Groups | 11 | 9 | 82% |
| Identities | 15 | 11 | 73% |
| Venues | 7 | 5 | 71% |
| VLAN Pools | 17 | 10 | 59% |
| DPSK Services | 11 | 5 | 45% |
| L3 ACL Policies | 10 | 5 | 50% |
| Switch VLANs | 19 | 5 | 26% |
| Switches | 20 | 6 | 30% |
| WiFi Networks | 24 | 12 | 50% |
| RADIUS Profile | 12 | 4 | 33% |
| Certificate Template | 21 | 3 | 14% |
| APs | 106 | 15 | 14% |
| 188 other groups | 1,184 | 0 | 0% |

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
