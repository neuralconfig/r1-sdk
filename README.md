# R1 Python SDK

A Python SDK for the RUCKUS One (R1) network management platform API.

> **Alpha** — This SDK covers ~8% of the R1 API (1,491 operations across 203 tag groups). Core modules for venues, APs, switches, WiFi networks, VLAN pools, DPSK, identities, L3 ACL policies, CLI templates, and switch profiles are implemented. See [API Coverage](#api-coverage) for details.

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

## API Modules

| Module | Access via | Key Methods |
|--------|-----------|-------------|
| Venues | `client.venues` | `list()`, `list_all()`, `get(id)`, `create()`, `update()`, `delete()` |
| Access Points | `client.aps` | `list(query)`, `list_all()`, `get(id)`, `reboot()` |
| Switches | `client.switches` | `list(query)`, `list_all()`, `get(id)`, `get_ports()` |
| WiFi Networks | `client.wifi_networks` | `list(query)`, `list_all()`, `get(id)`, `create()`, `update()` |
| VLAN Pools | `client.vlan_pools` | `list()`, `get()`, `create()` |
| DPSK | `client.dpsk` | `list_services()`, `list_passphrases()`, `create_passphrase()` |
| Identities | `client.identities` | `list()`, `list_all(group_id)`, `get()`, `create()`, `update()`, `delete()` |
| Identity Groups | `client.identity_groups` | `list()`, `list_all()`, `get()`, `create()` |
| L3 ACL Policies | `client.l3_acl_policies` | `list()`, `get()`, `create()`, `update()`, `delete()` |
| CLI Templates | `client.cli_templates` | `list()`, `list_all()`, `get()`, `create()` |
| Switch Profiles | `client.switch_profiles` | `list()`, `list_all()`, `get()`, `create()`, `update()` |

## API Coverage

The R1 API has **1,491 operations** across **203 tag groups**. The SDK covers **112 operations (~8%)** with full or partial coverage of 29 tag groups:

| Tag Group | Spec Ops | SDK Ops | Coverage |
|-----------|----------|---------|----------|
| CLI Templates | 10 | 10 | 100% |
| Switch Profiles | 10 | 10 | 100% |
| DPSK Passphrases | 14 | 11 | 79% |
| Identity Groups | 11 | 8 | 73% |
| Identities | 15 | 10 | 67% |
| Venues | 7 | 4 | 57% |
| VLAN Pools | 17 | 9 | 53% |
| L3 ACL Policies | 10 | 4 | 40% |
| DPSK Services | 11 | 5 | 45% |
| Switch VLANs | 19 | 4 | 21% |
| Switches | 20 | 4 | 20% |
| WiFi Networks | 24 | 4 | 17% |
| APs | 106 | 7 | 7% |
| 174 other groups | 1,077 | 0 | 0% |

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
