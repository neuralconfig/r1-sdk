# Switch Addition Script Examples

The `add_switch_to_venue.py` script allows you to add/preprovision switches to RUCKUS One venues.

## Prerequisites

1. Ensure you have valid RUCKUS One credentials configured
2. Activate the virtual environment: `source venv/bin/activate`

## Usage Examples

### 1. Command Line Mode (Recommended)

```bash
# Basic switch addition (name is required)
python add_switch_to_venue.py \
  --venue-id b918a78677f440f085f275f3a9ae3d2c \
  --serial FPT4814W009 \
  --name "Lab-ICX-Switch" \
  --yes

# With custom name and description
python add_switch_to_venue.py \
  --venue-id b918a78677f440f085f275f3a9ae3d2c \
  --serial FPT4814W009 \
  --name "Lab-ICX-Switch" \
  --description "Lab switch for testing" \
  --yes

# Advanced configuration
python add_switch_to_venue.py \
  --venue-id b918a78677f440f085f275f3a9ae3d2c \
  --serial FPT4814W009 \
  --name "Stack-Master-Switch" \
  --description "Main switch in stack configuration" \
  --enable-stack \
  --jumbo-mode \
  --initial-vlan-id 10 \
  --verbose \
  --yes
```

### 2. Interactive Mode

```bash
# Run without parameters for interactive prompts
python add_switch_to_venue.py
```

The script will prompt you for:
- Venue ID
- Switch serial number
- Switch name (optional)
- Description (optional)

### 3. Common Venue IDs

```bash
# Lab venue
--venue-id b918a78677f440f085f275f3a9ae3d2c
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--venue-id` | Target venue ID | Required |
| `--serial` | Switch serial number | Required |
| `--name` | Switch display name | **Required** |
| `--description` | Switch description | None |
| `--enable-stack` | Enable switch stacking | False |
| `--jumbo-mode` | Enable jumbo frames | False |
| `--no-igmp-snooping` | Disable IGMP snooping | False (enabled by default) |
| `--initial-vlan-id` | Initial VLAN ID | 1 |
| `--verbose, -v` | Show detailed output | False |
| `--yes, -y` | Skip confirmation prompt | False |

## Current API Status

⚠️ **Note**: Both switch addition endpoints currently return SWITCH-10000 errors, indicating potential restrictions or permissions requirements.

### Analysis Completed
- ✅ **Payload Structure**: Corrected based on analysis of existing switch FNS4352T0D4
- ✅ **Data Types**: Fixed to use proper booleans and strings (not empty strings)
- ✅ **Required Fields**: Identified that `name` is required
- ✅ **Field Values**: Use correct defaults (`igmpSnooping: "none"`, `specifiedType: "ROUTER"`)
- ✅ **Multiple Endpoints**: Discovered both documented and official Postman endpoints

### Discovered Endpoints

**1. Documented API Endpoint**: `POST /venues/{venueId}/switches`
- Found in official API documentation
- Complex payload with many configuration options
- Returns SWITCH-10000 error

**2. Official Postman Endpoint**: `POST /switches`
- Found in [RUCKUS One Postman Collection](https://github.com/commscope-ruckus/RUCKUS-One-Postman)
- Simple payload: `{"name": "...", "id": "...", "venueId": "...", "stackMembers": [], "trustPorts": []}`
- Also returns SWITCH-10000 error

Both implementations are correct but appear to require special permissions or account configuration.

## Error Handling

The script provides detailed error messages for common issues:

- **SWITCH-10000**: API endpoint restrictions
- **Validation Error**: Invalid parameters or existing switch
- **Resource Not Found**: Invalid venue ID or switch not found
- **Authentication Error**: Invalid credentials

## Troubleshooting

1. **API Errors**: Contact RUCKUS Support if SWITCH-10000 errors persist
2. **Credentials**: Verify `config.ini` or environment variables are set correctly
3. **Venue ID**: Use the venue list API to verify venue IDs
4. **Serial Numbers**: Ensure switch serial numbers are valid and not already provisioned