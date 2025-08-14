# RUCKUS One AP Reboot Manager

A comprehensive tool for safely managing Access Point reboots across your RUCKUS One deployment. This script provides export, simulation, and batch reboot capabilities with safety checks and resume functionality.

## Overview

The AP Reboot Manager allows you to:
- **Export** all Access Points from your tenant to CSV with current status
- **Review** and filter APs before rebooting
- **Simulate** reboot operations without making changes
- **Execute** controlled batch reboots with configurable delays
- **Resume** interrupted operations from checkpoints
- **Monitor** progress with colored output and countdown timers

## Prerequisites

- Python 3.7+ with virtual environment
- RUCKUS One API credentials configured in `config.ini`
- Access to RUCKUS One tenant with AP management permissions

## Installation

1. Ensure you're in the project virtual environment:
```bash
source venv/bin/activate
```

2. The script is ready to use: `ap_reboot_manager.py`

## Configuration

Create a `config.ini` file with your RUCKUS One credentials:

```ini
[credentials]
client_id = your-client-id
client_secret = your-client-secret  
tenant_id = your-tenant-id
region = na  # Options: na, eu, asia
```

## Quick Start

### Basic Workflow

1. **Export APs to CSV**
```bash
python3 ap_reboot_manager.py --config config.ini --export
```

2. **Review and edit the CSV** (remove APs you don't want to reboot)

3. **Test with simulation**
```bash
python3 ap_reboot_manager.py --config config.ini --import ap_export_20250811_123456.csv --simulate
```

4. **Execute actual reboot**
```bash
python3 ap_reboot_manager.py --config config.ini --import ap_export_20250811_123456.csv --delay 60 --force
```

## Detailed Usage

### Command Line Options

```
usage: ap_reboot_manager.py [-h] --config CONFIG [--export] [--import IMPORT_FILE] 
                           [--simulate] [--delay DELAY] [--output OUTPUT]
                           [--log-level {DEBUG,INFO,WARNING,ERROR}] [--log-file LOG_FILE]
                           [--force] [--resume] [--batch-size BATCH_SIZE] 
                           [--skip-status-check]

Required Arguments:
  --config CONFIG              Path to config.ini file with RUCKUS One credentials

Mode Selection (choose one):
  --export                     Export all APs to CSV with current status and details
  --import IMPORT_FILE         Import CSV file and reboot APs listed in it

Operation Options:
  --simulate                   Simulate mode: show what would be done without actual reboots
  --delay DELAY               Delay between reboots in seconds (default: 2, shows countdown)
  --force                     Required safety flag when rebooting more than 100 APs
  --skip-status-check         Skip runtime status verification and trust CSV status (faster, less safe)

Output Options:
  --output OUTPUT             Custom output filename for export (default: ap_export_YYYYMMDD_HHMMSS.csv)
  --log-level LEVEL           Set logging verbosity level (default: INFO)
  --log-file LOG_FILE         Write logs to specified file in addition to console

Recovery Options:
  --resume                    Resume from last checkpoint after interruption (use with --import)
  --batch-size BATCH_SIZE     Number of APs to process before saving checkpoint (default: 50)
```

### Export Mode

Export all Access Points from your tenant to a CSV file:

```bash
# Export with auto-generated filename
python3 ap_reboot_manager.py --config config.ini --export

# Export to custom filename  
python3 ap_reboot_manager.py --config config.ini --export --output my_aps.csv
```

**CSV Columns:**
- `serial_number` - AP serial number (used for reboot API calls)
- `mac_address` - AP MAC address
- `model` - AP hardware model
- `firmware_version` - Current firmware version
- `name` - AP display name
- `venue_id` - Venue ID (required for reboot API)
- `venue_name` - Human-readable venue name
- `ip_address` - Current IP address
- `status` - Current operational status

### Import and Reboot Mode

#### CSV Review and Filtering

Before rebooting, review the exported CSV:

1. **Check AP Status**: Only APs with operational status (starting with `2_` like `2_00_Operational`) will be rebooted
2. **Remove Unwanted APs**: Delete entire rows for APs you don't want to reboot
3. **Verify Venues**: Ensure APs are in the correct venues
4. **Save Changes**: Keep the same CSV format and column headers

#### Simulation Mode

**Always test with simulation first:**

```bash
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --simulate
```

Simulation mode will:
- Show exactly which APs would be rebooted
- Display the API calls that would be made
- Skip non-operational APs
- Apply delays and show countdown timers
- Generate summary tables

#### Live Reboot Mode

```bash
# Basic reboot with default 2-second delay
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv

# Reboot with 2-minute delay between APs
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --delay 120

# Required --force flag for >100 APs
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --delay 60 --force
```

### Safety Features

#### Status Checking

**Runtime Status Verification (Default):**
- Fetches current AP status before each reboot
- Compares with CSV status and reports changes
- Only reboots APs that are currently operational
- Caches results to minimize API calls

**Skip Status Check (Faster):**
```bash
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --skip-status-check
```

#### Safety Limits

- **100 AP Limit**: Requires `--force` flag for more than 100 APs
- **1000 AP Confirmation**: Interactive confirmation for more than 1000 APs
- **Operational Check**: Only operational APs are rebooted
- **Error Retry**: 3 attempts with exponential backoff for failed reboots

#### Graceful Interruption

**First CTRL+C**: Completes current operation and saves checkpoint
**Second CTRL+C**: Immediate forced shutdown

### Resume Functionality

If an operation is interrupted, resume from the last checkpoint:

```bash
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --resume --force
```

- Checkpoints are saved every 50 APs (configurable with `--batch-size`)
- Resume picks up from the last completed AP
- Statistics are preserved across resume

### Visual Feedback

#### Colored Output
- **AP Names**: Cyan and bold
- **Serial Numbers**: Yellow
- **Success**: Green
- **Errors**: Red  
- **Warnings**: Yellow
- **Status Changes**: Color-coded

#### Countdown Timer
During delays, shows visual countdown:
```
Waiting 60s before next AP: .........10.........20.........30.........40.........50.........60
```

#### Progress Indicators
```
[15/100] (15.0%) Processing AP: Office-R770-001 (SN: 123456789012)
```

#### Summary Tables

**Successfully Rebooted APs:**
```
AP Name                        Serial Number        Venue ID                            
--------------------------------------------------------------------------------
Office-R770-001                123456789012         xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx    
Bedroom-R770-002               987654321098         xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx    
```

**Skipped APs (Not Operational):**
```
AP Name                   Serial Number        Status                             
--------------------------------------------------------------------------------
T350-001                  555666777888         3_04_DisconnectedFromCloud         
T350-002                  444555666777         3_04_DisconnectedFromCloud         
```

## Examples

### Complete Workflow Example

```bash
# 1. Export all APs
python3 ap_reboot_manager.py --config config.ini --export --output office_aps.csv

# 2. Edit office_aps.csv (remove APs you don't want to reboot)

# 3. Simulate to verify  
python3 ap_reboot_manager.py --config config.ini --import office_aps.csv --simulate --delay 30

# 4. Execute with 5-minute delays
python3 ap_reboot_manager.py --config config.ini --import office_aps.csv --delay 300 --force

# 5. If interrupted, resume
python3 ap_reboot_manager.py --config config.ini --import office_aps.csv --delay 300 --force --resume
```

### Maintenance Window Example

```bash
# Export all APs for maintenance planning
python3 ap_reboot_manager.py --config config.ini --export --output maintenance_$(date +%Y%m%d).csv

# Test reboot sequence with 10-minute delays
python3 ap_reboot_manager.py --config config.ini --import maintenance_20250811.csv --simulate --delay 600

# Execute during maintenance window with logging
python3 ap_reboot_manager.py --config config.ini --import maintenance_20250811.csv --delay 600 --force --log-file maintenance.log --log-level DEBUG
```

### Troubleshooting Scenario

```bash
# Quick reboot of specific APs with minimal delay (after manual CSV filtering)
python3 ap_reboot_manager.py --config config.ini --import problem_aps.csv --delay 10 --skip-status-check
```

## Troubleshooting

### Common Issues

**Validation Errors:**
- Use `--skip-status-check` to avoid API validation issues
- Ensure config.ini has correct credentials and region

**Permission Errors:**
- Verify API credentials have AP management permissions
- Check tenant access for all venues in CSV

**Network Timeouts:**
- Increase delays between reboots
- Use `--batch-size` to save progress more frequently

**Large Deployments:**
- Process APs in smaller batches by filtering CSV
- Use `--skip-status-check` for faster processing
- Consider multiple maintenance windows

### Log Files

Enable detailed logging for troubleshooting:

```bash
python3 ap_reboot_manager.py --config config.ini --import my_aps.csv --log-level DEBUG --log-file reboot_debug.log
```

## API Details

### Reboot Endpoint
```
PATCH /venues/{venueId}/aps/{serialNumber}/systemCommands
Body: {"type": "REBOOT"}
```

### Status Codes
- **200**: Reboot initiated successfully
- **404**: AP not found (may be offline or moved)
- **400**: Invalid request or AP cannot be rebooted

## Security Considerations

- Store credentials securely in `config.ini`
- Use `--log-file` to maintain audit trail
- Test in simulate mode before production reboots
- Coordinate with network operations teams for large deployments
- Consider impact on users and services before mass reboots

## Performance Notes

- Runtime status checking adds ~1 second per unique venue
- Pre-caching optimizes status checks for multiple APs in same venue
- Use `--skip-status-check` for maximum speed when CSV is recent
- Default 2-second delay balances speed with network stability
- Checkpoint saves protect against data loss during long operations

---

*For technical support or feature requests, please refer to the project repository.*