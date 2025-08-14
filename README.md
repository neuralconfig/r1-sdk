# RUCKUS One (R1) Python SDK

A comprehensive Python SDK for interacting with the RUCKUS One (R1) network management system API.

> **⚠️ Work in Progress**
> 
> This SDK is currently under active development and does not provide 100% coverage of all RUCKUS One APIs. While it covers the most commonly used functionality for venues, access points, switches, WLANs, VLANs, and L3 ACL management, some advanced features may not be available yet.
> 
> **Experiencing issues?** Please [submit an issue on GitHub](https://github.com/yourusername/ruckus-one-sdk/issues) with detailed information about your use case and any problems encountered. Your feedback helps improve the SDK!

## Table of Contents

- [Features](#features)
- [Project Status](#project-status)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Modules](#api-modules)
- [L3 ACL Management](#l3-acl-management)
- [CSV Import Tool](#csv-import-tool)
- [CLI Tools](#cli-tools)
- [AP Reboot Manager](#ap-reboot-manager)
- [Utility Scripts](#utility-scripts)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [API Limitations](#api-limitations)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Comprehensive API Coverage**: Full support for RUCKUS One API endpoints
- **Pythonic Interface**: Intuitive, object-oriented design
- **Modular Architecture**: Organized by functional domains (venues, APs, switches, WLANs, VLANs, L3ACL)
- **OAuth2 Authentication**: Automatic token management and refresh
- **CLI Tools**: Both command-line and interactive modes
- **CSV Import**: Bulk L3 ACL policy creation from CSV files
- **Error Handling**: Custom exceptions with detailed error information
- **Logging Support**: Configurable logging for debugging and monitoring
- **Inventory Reporting**: Generate comprehensive network inventory reports

## Project Status

This SDK is **actively maintained** and provides solid coverage of core RUCKUS One functionality. Here's what's currently available:

### ✅ Fully Implemented
- **Core API Client**: OAuth2 authentication, error handling, request/response management
- **Venues Management**: Complete CRUD operations for venue management
- **Access Points**: Listing, monitoring, and basic management (including reboot functionality)
- **Switches**: Discovery, port management, and monitoring
- **WLANs**: Full wireless network configuration and management
- **VLANs**: VLAN pool creation and management
- **L3 ACL**: Comprehensive Layer-3 access control list management with CSV import
- **Identity Management**: User identity and group management
- **DPSK Management**: Dynamic Pre-Shared Key management
- **CLI Tools**: Both command-line and interactive interfaces
- **AP Reboot Manager**: Advanced batch AP management with safety features

### 🔄 Partial Implementation
- **Advanced AP Configuration**: Basic operations available, advanced configuration pending
- **Detailed Analytics**: Some reporting available, advanced analytics in development  
- **Event Management**: Basic event handling, advanced automation pending

### ❌ Not Yet Implemented
- **Advanced Switch Configuration**: Layer-3 switch features and advanced port management
- **Guest Management**: Guest portal and captive portal configuration
- **Advanced Monitoring**: Real-time monitoring dashboards and alerting
- **Firmware Management**: Device firmware updates and management
- **Site Survey Tools**: RF planning and site survey functionality

### API Coverage Estimate
- **Core Network Management**: ~85% coverage
- **Advanced Enterprise Features**: ~40% coverage  
- **Monitoring and Analytics**: ~60% coverage
- **Administrative Functions**: ~70% coverage

The SDK prioritizes reliability and ease of use over complete feature coverage. All implemented functionality is production-ready and thoroughly tested.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Development Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ruckus-one-sdk.git
   cd ruckus-one-sdk
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

## Quick Start

```python
from ruckus_one.client import RuckusOneClient

# Initialize client with API credentials
client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    region="na"  # "na", "eu", or "asia"
)

# List all venues
venues = client.venues.list()
print(f"Found {len(venues['data'])} venues")

# Create a new venue
new_venue = client.venues.create(
    name="Example Venue",
    address={
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zipCode": "94105",
        "country": "US"
    },
    description="Example venue for demonstration",
    timezone="America/Los_Angeles"
)

# Get access points in the venue
aps = client.aps.list(venue_id=new_venue['response']['id'])
print(f"Found {len(aps['data'])} APs in venue")

# Create an L3 ACL policy
l3_rules = [
    {
        "priority": 1,
        "description": "Allow HTTP traffic",
        "access": "ALLOW",
        "source": {"enableIpSubnet": False},
        "destination": {
            "enableIpSubnet": True,
            "ip": "192.168.1.0",
            "ipMask": "255.255.255.0",
            "port": "80"
        }
    }
]

acl_policy = client.l3acl.create(
    name="Example-ACL-Policy",
    l3_rules=l3_rules,
    description="Example L3 ACL policy",
    default_access="BLOCK"
)
```

## Authentication

The SDK supports multiple authentication methods using OAuth2 client credentials.

### Required Credentials

- **Client ID**: OAuth2 client identifier
- **Client Secret**: OAuth2 client secret
- **Tenant ID**: RUCKUS One tenant identifier
- **Region**: API region ("na", "eu", or "asia")

### Authentication Methods

#### 1. Direct Parameters

```python
client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    tenant_id="your-tenant-id",
    region="na"
)
```

#### 2. Environment Variables

```bash
export R1_CLIENT_ID="your-client-id"
export R1_CLIENT_SECRET="your-client-secret"
export R1_TENANT_ID="your-tenant-id"
export R1_REGION="na"
```

```python
import os
client = RuckusOneClient(
    client_id=os.environ.get("R1_CLIENT_ID"),
    client_secret=os.environ.get("R1_CLIENT_SECRET"),
    tenant_id=os.environ.get("R1_TENANT_ID"),
    region=os.environ.get("R1_REGION", "na")
)
```

#### 3. Configuration File

Create a `config.ini` file:

```ini
[credentials]
client_id = your-client-id
client_secret = your-client-secret
tenant_id = your-tenant-id
region = na
```

Load configuration in your code:

```python
import configparser
import os

def load_config(config_path="config.ini"):
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        if 'credentials' in config:
            return {
                'client_id': config['credentials'].get('client_id'),
                'client_secret': config['credentials'].get('client_secret'),
                'tenant_id': config['credentials'].get('tenant_id'),
                'region': config['credentials'].get('region', 'na')
            }
    return {}

config = load_config()
client = RuckusOneClient(**config)
```

## API Modules

The SDK is organized into modules, each handling specific RUCKUS One API domains:

### Venues Module (`client.venues`)

Manage physical locations and their properties.

```python
# List venues with pagination
venues = client.venues.list({"pageSize": 50, "page": 0})

# Get specific venue
venue = client.venues.get("venue-id-here")

# Create new venue
new_venue = client.venues.create(
    name="Branch Office",
    address={
        "street": "456 Business Ave",
        "city": "New York",
        "state": "NY",
        "zipCode": "10001",
        "country": "US"
    },
    timezone="America/New_York"
)

# Update venue
updated_venue = client.venues.update(
    venue_id="venue-id-here",
    name="Updated Branch Office"
)
```

### Access Points Module (`client.aps`)

Monitor and manage wireless access points.

```python
# List all APs
aps = client.aps.list()

# List APs in specific venue
venue_aps = client.aps.list(venue_id="venue-id-here")

# Get specific AP details
ap_details = client.aps.get("ap-id-here")

# Reboot an AP
reboot_response = client.aps.reboot("ap-id-here")
```

### Switches Module (`client.switches`)

Manage network switches and their configurations.

```python
# List switches
switches = client.switches.list()

# Get switch details
switch = client.switches.get("switch-id-here")

# List switch ports
ports = client.switches.list_ports("switch-id-here")
```

### WLANs Module (`client.wlans`)

Create and configure wireless networks.

```python
# List WLANs
wlans = client.wlans.list()

# Create new WLAN
new_wlan = client.wlans.create(
    name="Guest-Network",
    ssid="Guest-WiFi",
    vlanId=100,
    encryption="WPA2-Personal",
    passphrase="guestpassword123"
)

# Update WLAN
updated_wlan = client.wlans.update(
    wlan_id="wlan-id-here",
    name="Updated-Guest-Network"
)
```

### VLANs Module (`client.vlans`)

Manage VLAN configurations and pools.

```python
# List VLAN pools
vlan_pools = client.vlans.list_pools()

# Create VLAN pool
new_pool = client.vlans.create_vlan_pool(
    name="Office-VLANs",
    vlans=[
        {"id": 100, "name": "Users"},
        {"id": 200, "name": "Servers"}
    ]
)
```

### Identity Groups Module (`client.identity_groups`)

Manage user identity groups for access control.

```python
# List identity groups
groups = client.identity_groups.list()

# Create identity group
new_group = client.identity_groups.create(
    name="Employees",
    description="Employee access group"
)
```

### Identities Module (`client.identities`)

Manage individual user identities.

```python
# List identities
identities = client.identities.list()

# Create identity
new_identity = client.identities.create(
    username="john.doe",
    email="john.doe@company.com",
    groupId="group-id-here"
)
```

### DPSK Module (`client.dpsk`)

Manage Dynamic Pre-Shared Keys for secure wireless access.

```python
# List DPSK entries
dpsks = client.dpsk.list()

# Create DPSK
new_dpsk = client.dpsk.create(
    wlanId="wlan-id-here",
    username="guest-user",
    expirationDate="2024-12-31"
)
```

## L3 ACL Management

The L3 ACL module provides comprehensive Layer-3 Access Control List management.

### Basic L3 ACL Operations

```python
# List L3 ACL policies
policies = client.l3acl.list()

# Get specific policy
policy = client.l3acl.get("policy-id-here")

# Create L3 ACL policy
rules = [
    {
        "priority": 1,
        "description": "Allow web traffic to DMZ",
        "access": "ALLOW",
        "source": {"enableIpSubnet": False},
        "destination": {
            "enableIpSubnet": True,
            "ip": "192.168.100.0",
            "ipMask": "255.255.255.0",
            "port": "80"
        }
    },
    {
        "priority": 2,
        "description": "Allow HTTPS to DMZ",
        "access": "ALLOW", 
        "source": {"enableIpSubnet": False},
        "destination": {
            "enableIpSubnet": True,
            "ip": "192.168.100.0",
            "ipMask": "255.255.255.0",
            "port": "443"
        }
    }
]

new_policy = client.l3acl.create(
    name="DMZ-Access-Policy",
    l3_rules=rules,
    description="Allow web access to DMZ servers",
    default_access="BLOCK"  # Block all other traffic
)
```

### Rule Structure

L3 ACL rules have the following structure:

```python
rule = {
    "priority": 1,                    # Rule priority (1-128)
    "description": "Rule description",
    "access": "ALLOW",               # "ALLOW" or "BLOCK"
    "source": {
        "enableIpSubnet": False,     # True for specific subnet, False for any
        "ip": "10.0.0.0",           # Source IP (if enableIpSubnet=True)
        "ipMask": "255.255.255.0",  # Source mask (if enableIpSubnet=True)
        "port": "80"                 # Source port (optional)
    },
    "destination": {
        "enableIpSubnet": True,      # True for specific subnet, False for any
        "ip": "192.168.1.0",        # Destination IP
        "ipMask": "255.255.255.0",  # Destination mask
        "port": "443"                # Destination port (optional)
    }
}
```

### Creating Rules with Helper Method

```python
# Use the helper method to create rules
rule = client.l3acl.create_rule(
    description="Allow SSH to management network",
    priority=10,
    access="ALLOW",
    destination_enable_ip_subnet=True,
    destination_ip="10.0.1.0",
    destination_ip_mask="255.255.255.0",
    destination_port="22"
)
```

## CSV Import Tool

The SDK includes a powerful CSV import tool for bulk L3 ACL policy creation.

### CSV Format

Your CSV file should have the following format:

```csv
IPAddressRange,Port
192.168.1.0/24,80
192.168.1.0/24,443
10.0.0.0/8,22
172.16.0.0/12,3389
```

### Basic Usage

```bash
# Import CSV file to create L3 ACL policy
python3 import_l3acl_csv.py --csv-file data/endpoints.csv --policy-name "Corporate-Access"

# Use custom description
python3 import_l3acl_csv.py --csv-file data/endpoints.csv --policy-name "Corporate-Access" --description "Corporate network access policy"

# Dry run to preview what will be created
python3 import_l3acl_csv.py --csv-file data/endpoints.csv --policy-name "Corporate-Access" --dry-run
```

### Handling Large CSV Files (>128 Rules)

L3 ACL policies have a maximum of 128 rules. For larger CSV files, use the `--split-policies` option:

```bash
# Automatically split large CSV into multiple policies
python3 import_l3acl_csv.py --csv-file data/large-endpoints.csv --policy-name "MS-Endpoints" --split-policies

# This creates: MS-Endpoints-1, MS-Endpoints-2, etc.
```

### CSV Import Options

```bash
# All available options
python3 import_l3acl_csv.py \
  --csv-file data/endpoints.csv \
  --policy-name "My-Policy" \
  --description "Custom description" \
  --config config.ini \
  --region na \
  --split-policies \
  --dry-run \
  --verbose
```

### Authentication for CSV Import

The CSV import tool supports the same authentication methods:

```bash
# Using config file
python3 import_l3acl_csv.py --csv-file data/endpoints.csv --policy-name "Test" --config config.ini

# Using environment variables
export R1_CLIENT_ID="your-client-id"
export R1_CLIENT_SECRET="your-client-secret"
export R1_TENANT_ID="your-tenant-id"
python3 import_l3acl_csv.py --csv-file data/endpoints.csv --policy-name "Test"
```

## CLI Tools

The SDK provides both command-line and interactive CLI interfaces.

### Command-Line Mode

Execute individual commands directly:

```bash
# List venues
bin/ruckus-cli venue list --config config.ini

# Get venue details  
bin/ruckus-cli venue get --id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --config config.ini

# List APs in venue
bin/ruckus-cli ap list --venue-id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 --config config.ini

# Create WLAN
bin/ruckus-cli wlan create --name "Guest-WiFi" --ssid "Guest" --config config.ini
```

### Interactive Mode

Network switch-like interface with tab completion and help:

```bash
# Start interactive mode
bin/ruckus-cli --interactive --config config.ini
```

Interactive session example:

```
RUCKUS> authenticate --config config.ini
Successfully authenticated with RUCKUS One API
Region: na
Tenant ID: 12a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7

RUCKUS(na)> list_venues

Venues:
ID                                   | Name                    | City          | Country   
------------------------------------------------------------------------------------------
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6    | Example Test Venue     | San Francisco | US       

RUCKUS(na)> help
# Shows all available commands with categories

RUCKUS(na)> list_aps --venue-id a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
# Lists APs in the specified venue
```

## AP Reboot Manager

The SDK includes a comprehensive AP Reboot Manager tool for safely managing bulk Access Point reboots across your RUCKUS One deployment.

### Features

- **Export**: Generate CSV inventory of all Access Points with current status
- **Review & Filter**: Edit CSV to select specific APs for reboot operations  
- **Simulation Mode**: Preview operations without making actual changes
- **Batch Processing**: Execute controlled reboots with configurable delays
- **Resume Capability**: Continue interrupted operations from checkpoints
- **Safety Checks**: Prevents accidental mass reboots with confirmation prompts
- **Progress Monitoring**: Visual progress bars and countdown timers

### Quick Start

```bash
# 1. Export all APs to CSV for review
python3 ap_reboot_manager.py --config config.ini --export

# 2. Edit the generated CSV to select APs for reboot

# 3. Simulate the reboot operation (dry run)
python3 ap_reboot_manager.py --config config.ini --import ap_export_20250814_123456.csv --simulate

# 4. Execute the actual reboot with 60-second delays
python3 ap_reboot_manager.py --config config.ini --import ap_export_20250814_123456.csv --delay 60 --force
```

### Export Mode

Export all Access Points from your tenant:

```bash
# Export with default filename (includes timestamp)
python3 ap_reboot_manager.py --config config.ini --export

# Export with custom filename
python3 ap_reboot_manager.py --config config.ini --export --output my_ap_inventory.csv
```

The exported CSV includes:
- AP ID, Name, Serial Number
- Model, Hardware Version, Firmware Version
- Venue ID and Name
- Current Status (ONLINE, OFFLINE, etc.)
- Connection Status and Last Seen
- Management IP Address

### Import and Reboot Mode

Process a CSV file to reboot selected APs:

```bash
# Simulation mode (safe testing)
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv --simulate

# Execute with default 2-second delay
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv

# Execute with custom delay between reboots
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv --delay 120

# For large operations (100+ APs), use --force flag
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv --delay 60 --force
```

### Recovery and Resume

If an operation is interrupted, resume from the last checkpoint:

```bash
# Resume interrupted reboot operation
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv --resume --delay 60

# Adjust checkpoint frequency (default: 50 APs)
python3 ap_reboot_manager.py --config config.ini --import ap_list.csv --batch-size 25
```

### Safety Features

- **Simulation Mode**: Test operations without making changes
- **Confirmation Prompts**: Requires explicit confirmation for large operations
- **Status Verification**: Checks AP status before attempting reboot
- **Checkpoint System**: Saves progress to enable resume after interruption
- **Detailed Logging**: Comprehensive logs for troubleshooting and audit trails

### Command Line Options

```bash
# Required
--config CONFIG              # Path to credentials configuration file

# Mode Selection (choose one)
--export                     # Export all APs to CSV
--import IMPORT_FILE         # Import CSV and reboot listed APs

# Operation Options
--simulate                   # Dry run mode - no actual reboots
--delay SECONDS             # Delay between reboots (default: 2)
--force                     # Required for operations with 100+ APs
--skip-status-check         # Skip runtime status verification (faster, less safe)

# Recovery Options  
--resume                    # Resume from last checkpoint
--batch-size SIZE           # Checkpoint frequency (default: 50)

# Output Options
--output FILENAME           # Custom export filename
--log-level LEVEL          # Logging verbosity (DEBUG, INFO, WARNING, ERROR)
--log-file FILENAME        # Write logs to file
```

### Best Practices

1. **Always export first**: Get current inventory and status before planning reboots
2. **Use simulation mode**: Test your CSV and parameters before execution
3. **Set appropriate delays**: Allow time for APs to fully restart (recommended: 60+ seconds)
4. **Monitor operations**: Watch for failed reboots and address connectivity issues
5. **Schedule during maintenance windows**: Avoid rebooting APs during peak usage
6. **Keep logs**: Enable log files for troubleshooting and compliance

### Example Workflow

```bash
# Step 1: Export current AP inventory
python3 ap_reboot_manager.py --config config.ini --export --output campus_aps.csv

# Step 2: Edit CSV - remove APs you don't want to reboot, save as reboot_list.csv

# Step 3: Test the operation
python3 ap_reboot_manager.py --config config.ini --import reboot_list.csv --simulate

# Step 4: Execute with logging
python3 ap_reboot_manager.py --config config.ini --import reboot_list.csv --delay 90 --force --log-file reboot_operation.log

# Step 5: If interrupted, resume
python3 ap_reboot_manager.py --config config.ini --import reboot_list.csv --resume --delay 90 --log-file reboot_operation.log
```

## Utility Scripts

The SDK includes several utility scripts for network management and analysis:

### Inventory Report Generator

Generate comprehensive network inventory reports:

```bash
python3 inventory_report.py
```

Features:
- Complete network device inventory
- Venue-based organization
- Device status and health information
- Exportable format for documentation

### WLAN Information Analyzer

Analyze WLAN configurations and relationships:

```bash
python3 wlan_info.py
```

Provides:
- WLAN configuration details
- SSID mappings
- Security settings analysis
- Venue associations

### WLAN-Venue Relationship Analyzer

Debug WLAN-venue relationships:

```bash
python3 wlan_venue_info.py
```

Helps with:
- Understanding WLAN-venue associations
- Troubleshooting connectivity issues
- Venue-specific WLAN configurations

## Testing

The SDK includes comprehensive test suites for all modules.

### Running Individual Tests

```bash
# Test authentication
python3 test_authentication.py

# Test specific modules
python3 test_ap_access.py
python3 test_switch_vlans.py
python3 test_wlan_access.py
python3 test_vlan_access.py

# Test L3ACL functionality
python3 test_l3acl.py
```

### Running Module-Specific Tests

```bash
# Run tests for specific API modules
python3 test_modules/test_venues.py
python3 test_modules/test_access_points.py
python3 test_modules/test_switches.py
python3 test_modules/test_wlans.py
python3 test_modules/test_vlans.py
python3 test_modules/test_identities.py
python3 test_modules/test_identity_groups.py

# Run all module tests
python3 test_modules/run_all_tests.py
```

### Test Configuration

Tests use the same authentication methods as the main SDK. Create a test configuration:

```ini
[credentials]
client_id = your-test-client-id
client_secret = your-test-client-secret
tenant_id = your-test-tenant-id
region = na
```

## API Limitations

### L3 ACL Policies

- **Maximum Rules**: 128 rules per policy
- **Priority Range**: 1-128 (lower number = higher priority)
- **Rule Limit Handling**: Use `--split-policies` option in CSV import for large datasets

### Rate Limiting

- The RUCKUS One API implements rate limiting
- SDK automatically handles retries for rate limit responses
- For bulk operations, consider adding delays between requests

### Asynchronous Operations

Many operations are asynchronous and return a `requestId`:

```python
response = client.venues.create(name="New Venue", ...)
if 'requestId' in response:
    request_id = response['requestId']
    # Poll activity API for completion status
    # activity = client.get(f"/activity/{request_id}")
```

## Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
from ruckus_one.exceptions import (
    APIError,
    AuthenticationError, 
    ResourceNotFoundError,
    ValidationError,
    RateLimitError,
    ServerError
)

try:
    venue = client.venues.get("non-existent-id")
except ResourceNotFoundError as e:
    print(f"Venue not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Invalid request: {e}")
except APIError as e:
    print(f"API error: {e}")
```

### Common Error Scenarios

```python
# Handle L3 ACL rule limit exceeded
try:
    policy = client.l3acl.create(name="Test", l3_rules=large_rule_list)
except ValueError as e:
    if "Too many L3 rules" in str(e):
        print("Rule limit exceeded. Consider using --split-policies option.")
    raise

# Handle rate limiting
try:
    for venue in venues:
        aps = client.aps.list(venue_id=venue['id'])
        # Process APs...
except RateLimitError as e:
    print("Rate limit exceeded. Retrying after delay...")
    time.sleep(60)  # Wait before retrying
```

## Examples

### Complete Venue Setup

```python
# Create venue with full configuration
venue = client.venues.create(
    name="Corporate HQ",
    address={
        "street": "100 Technology Drive",
        "city": "San Jose", 
        "state": "CA",
        "zipCode": "95110",
        "country": "US"
    },
    description="Main corporate headquarters",
    timezone="America/Los_Angeles"
)

venue_id = venue['response']['id']

# Create VLAN pool for the venue
vlan_pool = client.vlans.create_vlan_pool(
    name="HQ-VLANs",
    vlans=[
        {"id": 100, "name": "Employees"},
        {"id": 200, "name": "Guests"},
        {"id": 300, "name": "IoT"}
    ]
)

# Create WLANs
employee_wlan = client.wlans.create(
    name="Employee-WiFi",
    ssid="Corp-WiFi",
    vlanId=100,
    encryption="WPA2-Enterprise"
)

guest_wlan = client.wlans.create(
    name="Guest-WiFi", 
    ssid="Guest",
    vlanId=200,
    encryption="WPA2-Personal",
    passphrase="GuestPass123!"
)
```

### Bulk AP Management

```python
# Get all APs in venue
aps = client.aps.list(venue_id="venue-id-here")

# Filter APs by model
r770_aps = [ap for ap in aps['data'] if 'R770' in ap.get('model', '')]

# Reboot specific AP models
for ap in r770_aps:
    try:
        response = client.aps.reboot(ap['id'])
        print(f"Rebooted {ap['name']}: {response.get('requestId')}")
    except Exception as e:
        print(f"Failed to reboot {ap['name']}: {e}")
```

### Network Inventory Report

```python
# Generate complete network inventory
venues = client.venues.list()['data']

inventory = {}
for venue in venues:
    venue_id = venue['id']
    venue_name = venue['name']
    
    # Get devices in venue
    aps = client.aps.list(venue_id=venue_id)['data']
    switches = client.switches.list(venue_id=venue_id)['data']
    wlans = [w for w in client.wlans.list()['data'] if w.get('venueId') == venue_id]
    
    inventory[venue_name] = {
        'location': venue.get('address', {}),
        'access_points': len(aps),
        'switches': len(switches),
        'wlans': len(wlans),
        'devices': {
            'aps': [(ap['name'], ap['serialNumber']) for ap in aps],
            'switches': [(sw['name'], sw['serialNumber']) for sw in switches]
        }
    }

# Print inventory summary
for venue_name, info in inventory.items():
    print(f"\n{venue_name}:")
    print(f"  APs: {info['access_points']}")
    print(f"  Switches: {info['switches']}")
    print(f"  WLANs: {info['wlans']}")
```

### Enterprise Network Deployment

Complete example of setting up an enterprise network with proper error handling:

```python
import logging
from ruckus_one.client import RuckusOneClient
from ruckus_one.exceptions import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_enterprise_network():
    """Deploy a complete enterprise network configuration."""
    try:
        # Initialize client with error handling
        client = RuckusOneClient(
            client_id="your-client-id",
            client_secret="your-client-secret",
            tenant_id="your-tenant-id",
            region="na"
        )
        
        # Create venue with validation
        logger.info("Creating main campus venue...")
        venue_data = {
            "name": "Main Campus",
            "address": {
                "street": "123 Enterprise Way",
                "city": "San Francisco",
                "state": "CA",
                "zipCode": "94105",
                "country": "US"
            },
            "description": "Primary corporate campus location",
            "timezone": "America/Los_Angeles"
        }
        
        venue = client.venues.create(**venue_data)
        venue_id = venue['response']['id']
        logger.info(f"Created venue: {venue_id}")
        
        # Create VLAN pool for network segmentation
        logger.info("Setting up VLAN pool...")
        vlan_pool = client.vlans.create_vlan_pool(
            name="Enterprise-VLANs",
            vlans=[
                {"id": 10, "name": "Management"},
                {"id": 100, "name": "Employees"}, 
                {"id": 200, "name": "Guests"},
                {"id": 300, "name": "IoT"},
                {"id": 400, "name": "Servers"}
            ]
        )
        logger.info("VLAN pool created successfully")
        
        # Create employee identity group
        logger.info("Setting up identity management...")
        employee_group = client.identity_groups.create(
            name="Corporate Employees",
            description="Full-time corporate employees with standard access"
        )
        
        # Create secure employee WLAN
        logger.info("Creating employee WLAN...")
        employee_wlan = client.wlans.create(
            name="Corp-WiFi-Employee",
            ssid="CorpNet",
            vlanId=100,
            encryption="WPA2-Enterprise",
            description="Primary employee wireless network"
        )
        
        # Create guest WLAN with captive portal
        logger.info("Creating guest WLAN...")
        guest_wlan = client.wlans.create(
            name="Corp-WiFi-Guest",
            ssid="Guest-WiFi",
            vlanId=200,
            encryption="WPA2-Personal",
            passphrase="GuestAccess2024!",
            description="Guest access with time-limited sessions"
        )
        
        # Create L3 ACL for guest network restrictions
        logger.info("Setting up guest network restrictions...")
        guest_acl_rules = [
            {
                "priority": 1,
                "description": "Allow DNS",
                "access": "ALLOW",
                "source": {"enableIpSubnet": False},
                "destination": {
                    "enableIpSubnet": False,
                    "port": "53"
                }
            },
            {
                "priority": 2,
                "description": "Allow HTTP",
                "access": "ALLOW", 
                "source": {"enableIpSubnet": False},
                "destination": {
                    "enableIpSubnet": False,
                    "port": "80"
                }
            },
            {
                "priority": 3,
                "description": "Allow HTTPS",
                "access": "ALLOW",
                "source": {"enableIpSubnet": False},
                "destination": {
                    "enableIpSubnet": False,
                    "port": "443"
                }
            },
            {
                "priority": 4,
                "description": "Block internal networks",
                "access": "BLOCK",
                "source": {"enableIpSubnet": False},
                "destination": {
                    "enableIpSubnet": True,
                    "ip": "10.0.0.0",
                    "ipMask": "255.0.0.0"
                }
            }
        ]
        
        guest_acl = client.l3acl.create(
            name="Guest-Network-Policy",
            l3_rules=guest_acl_rules,
            description="Restrict guest access to internet only",
            default_access="BLOCK"
        )
        
        logger.info("Enterprise network deployment completed successfully!")
        
        # Return deployment summary
        return {
            "venue_id": venue_id,
            "employee_wlan_id": employee_wlan.get('response', {}).get('id'),
            "guest_wlan_id": guest_wlan.get('response', {}).get('id'),
            "guest_acl_request_id": guest_acl.get('requestId')
        }
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        logger.error("Please check your client credentials and tenant ID")
        raise
    
    except ValidationError as e:
        logger.error(f"Invalid configuration: {e}")
        logger.error("Please verify all required fields and formats")
        raise
        
    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        logger.info("Retrying after delay...")
        import time
        time.sleep(60)
        # Could implement retry logic here
        raise
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        logger.error("Rolling back any partial configuration...")
        # Could implement rollback logic here
        raise

# Execute deployment
if __name__ == "__main__":
    try:
        result = deploy_enterprise_network()
        print(f"Deployment successful! Summary: {result}")
    except Exception as e:
        print(f"Deployment failed: {e}")
```

### Automated AP Health Monitoring

Example of building a monitoring system with the SDK:

```python
import time
import logging
from datetime import datetime, timedelta
from ruckus_one.client import RuckusOneClient
from ruckus_one.exceptions import *

class APHealthMonitor:
    """Monitor AP health and perform automated actions."""
    
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(__name__)
        
    def check_ap_health(self, venue_id=None, reboot_threshold_hours=24):
        """
        Check AP health and reboot unhealthy APs.
        
        Args:
            venue_id: Specific venue to monitor (None for all venues)
            reboot_threshold_hours: Reboot APs offline for this many hours
        """
        try:
            # Get APs to monitor
            if venue_id:
                aps_response = self.client.aps.list(venue_id=venue_id)
            else:
                aps_response = self.client.aps.list()
                
            aps = aps_response.get('data', [])
            self.logger.info(f"Monitoring {len(aps)} access points")
            
            unhealthy_aps = []
            offline_threshold = datetime.now() - timedelta(hours=reboot_threshold_hours)
            
            # Analyze each AP
            for ap in aps:
                ap_id = ap.get('id')
                ap_name = ap.get('name', 'Unknown')
                status = ap.get('status', 'UNKNOWN')
                last_seen = ap.get('lastSeen')
                
                # Check if AP is offline too long
                if status != 'ONLINE':
                    if last_seen:
                        try:
                            last_seen_time = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                            if last_seen_time < offline_threshold:
                                unhealthy_aps.append({
                                    'id': ap_id,
                                    'name': ap_name,
                                    'status': status,
                                    'last_seen': last_seen,
                                    'issue': 'offline_too_long'
                                })
                        except ValueError:
                            self.logger.warning(f"Invalid last_seen format for AP {ap_name}: {last_seen}")
                
                # Could add more health checks here:
                # - High CPU usage
                # - Memory issues  
                # - Client count anomalies
                # - Signal strength problems
                
            # Take action on unhealthy APs
            if unhealthy_aps:
                self.logger.warning(f"Found {len(unhealthy_aps)} unhealthy APs")
                for ap in unhealthy_aps:
                    self.handle_unhealthy_ap(ap)
            else:
                self.logger.info("All APs are healthy")
                
            return {
                'total_aps': len(aps),
                'healthy_aps': len(aps) - len(unhealthy_aps),
                'unhealthy_aps': len(unhealthy_aps),
                'issues_found': unhealthy_aps
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            raise
    
    def handle_unhealthy_ap(self, ap_info):
        """Handle an unhealthy AP with appropriate action."""
        ap_id = ap_info['id']
        ap_name = ap_info['name']
        issue = ap_info['issue']
        
        try:
            if issue == 'offline_too_long':
                self.logger.info(f"Attempting to reboot offline AP: {ap_name}")
                
                # Attempt reboot
                reboot_response = self.client.aps.reboot(ap_id)
                request_id = reboot_response.get('requestId')
                
                if request_id:
                    self.logger.info(f"Reboot initiated for {ap_name}, requestId: {request_id}")
                else:
                    self.logger.warning(f"Reboot response unclear for {ap_name}: {reboot_response}")
                    
        except ResourceNotFoundError:
            self.logger.error(f"AP {ap_name} not found - may have been deleted")
        except Exception as e:
            self.logger.error(f"Failed to handle unhealthy AP {ap_name}: {e}")
    
    def run_continuous_monitoring(self, interval_minutes=15, venue_id=None):
        """Run continuous monitoring loop."""
        self.logger.info(f"Starting continuous monitoring (interval: {interval_minutes} min)")
        
        while True:
            try:
                self.logger.info("--- Starting health check cycle ---")
                result = self.check_ap_health(venue_id=venue_id)
                self.logger.info(f"Health check complete: {result['healthy_aps']}/{result['total_aps']} APs healthy")
                
                # Wait for next cycle
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring cycle failed: {e}")
                self.logger.info("Retrying in 5 minutes...")
                time.sleep(300)  # Wait 5 minutes before retry

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    client = RuckusOneClient(
        client_id="your-client-id",
        client_secret="your-client-secret", 
        tenant_id="your-tenant-id",
        region="na"
    )
    
    monitor = APHealthMonitor(client)
    
    # Run one-time health check
    result = monitor.check_ap_health()
    print(f"Health check results: {result}")
    
    # Or run continuous monitoring
    # monitor.run_continuous_monitoring(interval_minutes=30)
```

### CSV Data Integration Workflow

Example of integrating external data sources with L3 ACL management:

```python
import csv
import ipaddress
import logging
from pathlib import Path
from ruckus_one.client import RuckusOneClient
from ruckus_one.exceptions import *

def process_security_feed_to_acl(csv_file_path, client, policy_name="Security-Blocklist"):
    """
    Process a security threat feed CSV and create/update L3 ACL policies.
    
    Expected CSV format:
    ThreatIP,Category,Severity,Description
    192.168.1.100,malware,high,"Known C&C server"
    10.0.0.50,botnet,medium,"Compromised host"
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Parse threat feed CSV
        threats = []
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                threat_ip = row.get('ThreatIP', '').strip()
                category = row.get('Category', 'unknown').strip()
                severity = row.get('Severity', 'medium').strip()
                description = row.get('Description', '').strip()
                
                # Validate IP address
                try:
                    ipaddress.ip_address(threat_ip)
                    threats.append({
                        'ip': threat_ip,
                        'category': category,
                        'severity': severity,
                        'description': description
                    })
                except ValueError:
                    logger.warning(f"Invalid IP address skipped: {threat_ip}")
        
        logger.info(f"Parsed {len(threats)} valid threat entries")
        
        # Create L3 ACL rules to block threats
        rules = []
        priority = 1
        
        # Group by severity for better rule organization
        high_threats = [t for t in threats if t['severity'].lower() == 'high']
        medium_threats = [t for t in threats if t['severity'].lower() == 'medium'] 
        low_threats = [t for t in threats if t['severity'].lower() == 'low']
        
        # Process high-priority threats first
        for threat_list, severity_name in [(high_threats, 'HIGH'), (medium_threats, 'MED'), (low_threats, 'LOW')]:
            for threat in threat_list:
                if priority > 128:  # L3 ACL rule limit
                    logger.warning(f"Rule limit reached, truncating at {priority-1} rules")
                    break
                    
                rule = {
                    "priority": priority,
                    "description": f"Block {severity_name}: {threat['category']} - {threat['description'][:50]}",
                    "access": "BLOCK",
                    "source": {
                        "enableIpSubnet": True,
                        "ip": threat['ip'],
                        "ipMask": "255.255.255.255"  # Single host
                    },
                    "destination": {
                        "enableIpSubnet": False
                    }
                }
                rules.append(rule)
                priority += 1
        
        # Check if policy already exists
        try:
            existing_policies = client.l3acl.list()
            existing_policy = None
            
            for policy in existing_policies.get('data', []):
                if policy.get('name') == policy_name:
                    existing_policy = policy
                    break
            
            if existing_policy:
                # Update existing policy
                logger.info(f"Updating existing policy '{policy_name}' with {len(rules)} rules")
                response = client.l3acl.update(
                    l3acl_policy_id=existing_policy['id'],
                    name=policy_name,
                    l3_rules=rules,
                    description=f"Security threat blocklist - Updated {datetime.now().isoformat()}",
                    default_access="ALLOW"  # Allow all other traffic
                )
            else:
                # Create new policy
                logger.info(f"Creating new policy '{policy_name}' with {len(rules)} rules")
                response = client.l3acl.create(
                    name=policy_name,
                    l3_rules=rules,
                    description=f"Security threat blocklist - Created {datetime.now().isoformat()}",
                    default_access="ALLOW"  # Allow all other traffic
                )
            
            logger.info(f"L3 ACL policy operation completed: {response.get('requestId', 'No requestId')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create/update L3 ACL policy: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Security feed processing failed: {e}")
        raise

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = RuckusOneClient(
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id", 
        region="na"
    )
    
    # Process security feed and update firewall rules
    try:
        response = process_security_feed_to_acl(
            csv_file_path="data/threat_feed.csv",
            client=client,
            policy_name="Automated-Threat-Blocklist"
        )
        print(f"Security policy updated successfully: {response}")
        
    except Exception as e:
        print(f"Failed to update security policy: {e}")
```

## Troubleshooting

Common issues and solutions when using the RUCKUS One Python SDK.

### Authentication Issues

**Problem**: `AuthenticationError: Invalid credentials`
```
ruckus_one.exceptions.AuthenticationError: Authentication failed
```

**Solutions**:
1. **Verify credentials**: Double-check your client_id, client_secret, and tenant_id
2. **Check region**: Ensure you're using the correct region ("na", "eu", "asia")
3. **Test with cURL**:
   ```bash
   curl -X POST https://api-na.ruckus.cloud/oauth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&tenant_id=YOUR_TENANT_ID"
   ```

**Problem**: `AuthenticationError: Token expired`

**Solutions**:
- The SDK handles token refresh automatically
- If issues persist, recreate the client instance
- Check system clock synchronization

### API Rate Limiting

**Problem**: `RateLimitError: Too many requests`

**Solutions**:
1. **Add delays between requests**:
   ```python
   import time
   for item in large_list:
       result = client.api_call(item)
       time.sleep(1)  # 1-second delay
   ```

2. **Implement retry logic**:
   ```python
   from ruckus_one.exceptions import RateLimitError
   import time
   
   def api_call_with_retry(func, *args, max_retries=3, **kwargs):
       for attempt in range(max_retries):
           try:
               return func(*args, **kwargs)
           except RateLimitError as e:
               if attempt == max_retries - 1:
                   raise
               wait_time = 2 ** attempt  # Exponential backoff
               time.sleep(wait_time)
   ```

### Connection Issues

**Problem**: `ConnectionError: Failed to connect to API`

**Solutions**:
1. **Check network connectivity**: Verify internet access
2. **Check firewall**: Ensure HTTPS (443) traffic is allowed to:
   - `api-na.ruckus.cloud` (North America)
   - `api-eu.ruckus.cloud` (Europe) 
   - `api-asia.ruckus.cloud` (Asia)
3. **Proxy configuration**: If behind corporate proxy, configure requests:
   ```python
   import os
   os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'
   ```

### L3 ACL Issues

**Problem**: `ValueError: Too many L3 rules`

**Solutions**:
1. **Use split policies**: For CSV imports with >128 rules:
   ```bash
   python import_l3acl_csv.py --csv-file large.csv --policy-name "Policy" --split-policies
   ```

2. **Optimize rules**: Combine similar rules using broader IP ranges
3. **Multiple policies**: Create separate policies for different purposes

**Problem**: L3 ACL policy not taking effect

**Solutions**:
1. **Check policy assignment**: Ensure policy is assigned to the correct WLAN/network
2. **Verify rule order**: Lower priority numbers = higher precedence
3. **Test connectivity**: Use network tools to verify rule enforcement

### Resource Not Found Issues

**Problem**: `ResourceNotFoundError: Venue/AP/WLAN not found`

**Solutions**:
1. **Verify IDs**: Ensure you're using the correct resource ID
2. **Check permissions**: Verify your API credentials have access to the resource
3. **List resources**: Use list methods to find correct IDs:
   ```python
   # Find correct venue ID
   venues = client.venues.list()
   for venue in venues['data']:
       print(f"Name: {venue['name']}, ID: {venue['id']}")
   ```

### Asynchronous Operations

**Problem**: Operations return `requestId` but status is unclear

**Solutions**:
1. **Monitor via web portal**: Check RUCKUS One portal for request status
2. **Wait for completion**: Some operations take several minutes
3. **Implement polling** (when activity API becomes available):
   ```python
   # Future implementation when activity API is documented
   def wait_for_completion(request_id, timeout=300):
       # This will be implemented when API documentation is available
       pass
   ```

### CSV Import Issues

**Problem**: CSV import fails with parsing errors

**Solutions**:
1. **Check CSV format**: Ensure proper headers and data format:
   ```csv
   IPAddressRange,Port
   192.168.1.0/24,80
   10.0.0.0/8,443
   ```

2. **Validate IP addresses**: Ensure all IP ranges are valid CIDR notation
3. **Check file encoding**: Use UTF-8 encoding for CSV files
4. **Test with small files**: Start with a few entries to validate format

### Python Environment Issues

**Problem**: Import errors or missing dependencies

**Solutions**:
1. **Verify installation**:
   ```bash
   pip list | grep ruckus
   pip install -e .  # Reinstall in development mode
   ```

2. **Check Python version**: Requires Python 3.7+
   ```bash
   python --version
   ```

3. **Virtual environment**: Use isolated environments:
   ```bash
   python -m venv ruckus_env
   source ruckus_env/bin/activate  # Linux/Mac
   ruckus_env\Scripts\activate     # Windows
   pip install -e .
   ```

### Logging and Debugging

Enable verbose logging to diagnose issues:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable HTTP request logging
import urllib3
urllib3.disable_warnings()  # Disable SSL warnings if needed

# Your client code here
client = RuckusOneClient(...)
```

### Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: Search [GitHub Issues](https://github.com/yourusername/ruckus-one-sdk/issues)
2. **Enable debug logging**: Include debug output in issue reports
3. **Provide context**: Include code samples, error messages, and environment details
4. **Test with minimal example**: Create a simple reproduction case

## Known Limitations

While the SDK provides robust core functionality, there are some current limitations to be aware of:

### API Coverage Limitations
- **Switch Configuration**: Advanced Layer-3 switch features not yet implemented
- **Guest Portal**: Captive portal configuration requires manual setup via web interface
- **Firmware Management**: Device firmware updates must be done through RUCKUS One portal
- **Real-time Analytics**: Live monitoring dashboards not available via SDK
- **Advanced Reporting**: Complex reporting features limited to basic inventory

### SDK-Specific Limitations
- **Activity API**: Request status polling not yet implemented (use portal for monitoring)
- **Bulk Operations**: Limited batch processing for large-scale operations
- **Caching**: No built-in response caching (implement client-side if needed)
- **Async Support**: Synchronous operations only (no asyncio support)
- **WebSockets**: No real-time event streaming capabilities

### Performance Considerations
- **Rate Limiting**: API calls are subject to RUCKUS One rate limits
- **Large Datasets**: Pagination required for venues/APs with thousands of items
- **L3 ACL Rules**: 128 rule limit per policy (use split policies for larger sets)
- **Concurrent Operations**: No built-in concurrency management

### Authentication Limitations
- **Token Caching**: Tokens not persisted between sessions
- **Multi-tenant**: Single tenant per client instance
- **Role-based Access**: Limited to permissions of configured API client

## Roadmap

Planned features and improvements for future releases:

### Version 0.2.0 (Q2 2024)
- **Activity API Integration**: Monitor asynchronous operation status
- **Enhanced Error Handling**: More specific exception types and better error messages
- **Caching Layer**: Optional response caching for improved performance
- **Retry Logic**: Built-in retry mechanisms for transient failures
- **Advanced Switch Support**: Layer-3 configuration and port management

### Version 0.3.0 (Q3 2024)
- **Async Support**: Full asyncio compatibility for concurrent operations
- **Bulk Operations**: Batch processing for large-scale operations
- **Real-time Events**: WebSocket support for live monitoring
- **Enhanced CLI**: Interactive mode improvements and new commands
- **Guest Portal API**: Captive portal configuration support

### Version 0.4.0 (Q4 2024)
- **Advanced Analytics**: Extended reporting and analytics capabilities
- **Firmware Management**: Device firmware update support
- **Multi-tenant Support**: Single client managing multiple tenants
- **Performance Optimization**: Connection pooling and request optimization
- **Enhanced Documentation**: Interactive API explorer and more examples

### Long-term Goals (2025+)
- **Site Survey Tools**: RF planning and optimization features
- **Machine Learning**: Predictive analytics for network optimization
- **Integration Ecosystem**: Pre-built integrations with popular network tools
- **GraphQL Support**: Alternative query interface for complex data retrieval
- **Mobile SDK**: Native mobile app development support

### Community Contributions Welcome

We actively encourage community contributions in these areas:
- **Testing**: Help test new features across different environments
- **Documentation**: Improve examples, tutorials, and troubleshooting guides
- **Feature Requests**: Suggest new functionality based on real-world needs
- **Bug Reports**: Help identify and resolve issues
- **Integration Examples**: Share use cases and integration patterns

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow existing code style** and patterns
3. **Add tests** for new functionality
4. **Update documentation** for any API changes
5. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ruckus-one-sdk.git
cd ruckus-one-sdk

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run tests
python3 test_modules/run_all_tests.py
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all public methods
- Maintain consistent error handling patterns

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

We're committed to helping you successfully use the RUCKUS One Python SDK. Here's how to get help:

### Before Creating an Issue

1. **Check the Documentation**: Review this README and the [Troubleshooting](#troubleshooting) section
2. **Search Existing Issues**: Look through [existing issues](https://github.com/yourusername/ruckus-one-sdk/issues) for similar problems
3. **Test with Latest Version**: Ensure you're using the latest SDK version
4. **Check Project Status**: Review the [Known Limitations](#known-limitations) section

### Creating a New Issue

When creating a new issue, please include:

#### For Bug Reports
```
**Bug Description**
Brief description of the issue

**Environment**
- SDK Version: x.x.x
- Python Version: 3.x.x
- Operating System: Windows/Mac/Linux
- RUCKUS One Region: na/eu/asia

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What you expected to happen

**Actual Behavior**  
What actually happened

**Code Sample**
```python
# Minimal code sample that reproduces the issue
```

**Error Message/Logs**
Full error traceback with debug logging enabled

**Additional Context**
Any other relevant information
```

#### For Feature Requests
```
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why this feature would be valuable

**Proposed API**
Suggested SDK interface (if applicable)

**RUCKUS One Support**
Does the underlying API support this feature?

**Priority**
How important is this feature to your workflow?
```

#### For Questions/Help
```
**Question**
Clear description of what you're trying to accomplish

**What You've Tried**
Steps you've already attempted

**Code Sample**
Relevant code showing your approach

**Documentation Review**
Sections of documentation you've already checked
```

### Response Times

- **Bug Reports**: We aim to respond within 2-3 business days
- **Feature Requests**: Initial response within 1 week
- **Questions**: Response within 1-2 business days
- **Security Issues**: Please email directly for urgent security concerns

### Community Support

- **GitHub Discussions**: Use for general questions and community help
- **Stack Overflow**: Tag questions with `ruckus-one-sdk` for community visibility
- **Code Examples**: Share your integration examples to help others

### Commercial Support

For enterprise users requiring dedicated support:
- Priority bug fixing
- Custom feature development
- Integration consulting
- Direct support channels

Contact information for commercial support inquiries would be provided by the maintainers.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.