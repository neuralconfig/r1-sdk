# R1 Python SDK

A Python SDK for the RUCKUS One (R1) network management platform API.

> **Alpha** — This SDK covers ~5% of the R1 API (1528 operations). Core modules for venues, APs, switches, WLANs, VLANs, DPSK, identities, and L3 ACLs are implemented. See [API Coverage](#api-coverage) for details.

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

# List WLANs
wlans = client.wlans.list({"pageSize": 100, "page": 0})
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
| Venues | `client.venues` | `list()`, `get(id)`, `create()`, `update()`, `delete()` |
| Access Points | `client.aps` | `list(query)`, `get(id)`, `reboot()` |
| Switches | `client.switches` | `list(query)`, `get(id)`, `get_ports()` |
| WLANs | `client.wlans` | `list(query)`, `get(id)`, `create()`, `update()` |
| VLANs | `client.vlans` | `list_pools()`, `get_pool()`, `create_pool()` |
| DPSK | `client.dpsk` | `list_services()`, `list_passphrases()`, `create_passphrase()` |
| Identities | `client.identities` | `list()`, `get()`, `create()`, `update()`, `delete()` |
| Identity Groups | `client.identity_groups` | `list()`, `get()`, `create()` |
| L3 ACL | `client.l3acl` | `list()`, `get()`, `create()`, `update()`, `delete()` |
| CLI Templates | `client.cli_templates` | `list()`, `get()`, `create()` |
| Switch Profiles | `client.switch_profiles` | `list()`, `get()`, `create()`, `update()` |

## API Coverage

The R1 API has **1528 operations** across **29 tag groups**. Current SDK coverage:

| Tag Group | Operations | Coverage |
|-----------|-----------|----------|
| Wi-Fi API & Model Docs | 625 | ~5% |
| Switch Services | 244 | ~10% |
| DPSK Service | 34 | ~70% |
| Identity Management | 27 | ~60% |
| Venues | 20 | ~40% |
| Configuration Templates | 6 | ~20% |
| Tenant Management | 31 | <5% |
| 22 other groups | 541 | None |

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

# Integration tests (requires config.ini with valid credentials)
.venv/bin/pytest tests/integration/ -m integration -v
```

## License

MIT — see [LICENSE](LICENSE).
