#!/usr/bin/env python3
"""
RUCKUS One AP Reboot Manager.

This script provides comprehensive AP management capabilities including:
- Export all APs to CSV
- Import CSV and reboot APs with configurable delay
- Simulate mode for dry runs
- Resume capability for interrupted operations
- Support for thousands of APs with proper pagination
"""

import os
import sys
import csv
import json
import time
import signal
import logging
import argparse
import configparser
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.venues import Venues
from ruckus_one.modules.access_points import AccessPoints

# Configure logging
logger = logging.getLogger(__name__)

# ANSI color codes
COLORS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

def colored(text: str, color: str, bold: bool = False) -> str:
    """Apply color to text for terminal output."""
    if not sys.stdout.isatty():
        return text  # No colors if not a terminal
    color_code = COLORS.get(color.upper(), '')
    bold_code = COLORS['BOLD'] if bold else ''
    return f"{bold_code}{color_code}{text}{COLORS['RESET']}"

def countdown_with_dots(seconds: int, prefix: str = "Waiting"):
    """Show countdown with dots, printing 10s markers."""
    if seconds <= 0:
        return
    
    # Use print to ensure it goes through logger formatting
    print(f"{prefix}: ", end='', flush=True)
    
    for i in range(1, seconds + 1):
        if shutdown_requested:
            print(" [Interrupted]")
            break
            
        time.sleep(1)
        
        if i % 10 == 0:
            # Print the 10s marker
            print(str(i), end='', flush=True)
        else:
            # Print a dot
            print(".", end='', flush=True)
        
        # Add newline every 50 seconds for readability
        if i % 50 == 0 and i < seconds:
            print("\n          ", end='', flush=True)
    
    print()  # Final newline

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    if shutdown_requested:
        # Second CTRL+C - force exit
        logger.warning("Force shutdown requested. Exiting immediately...")
        sys.exit(1)
    shutdown_requested = True
    logger.info("Shutdown requested. Press CTRL+C again to force stop...")

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    handlers = [console_handler]
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    logging.basicConfig(level=level, handlers=handlers)

def load_config(config_path: str) -> Dict[str, str]:
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config.read(config_path)
    
    if 'credentials' in config:
        return {
            'client_id': config['credentials'].get('client_id'),
            'client_secret': config['credentials'].get('client_secret'),
            'tenant_id': config['credentials'].get('tenant_id'),
            'region': config['credentials'].get('region', 'na')
        }
    elif 'auth' in config:
        return {
            'client_id': config['auth'].get('client_id'),
            'client_secret': config['auth'].get('client_secret'),
            'tenant_id': config['auth'].get('tenant_id'),
            'region': config['auth'].get('region', 'na')
        }
    else:
        raise ValueError("No credentials or auth section found in config file")

def get_all_aps(ap_module: AccessPoints, venues_dict: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Fetch all APs with proper pagination.
    
    Args:
        ap_module: AccessPoints module instance
        venues_dict: Dictionary mapping venue IDs to venue names
        
    Returns:
        List of all APs with venue information
    """
    all_aps = []
    page = 0
    page_size = 100
    total_pages = None
    
    logger.info("Starting to fetch all APs from tenant...")
    
    while True:
        if shutdown_requested:
            logger.warning("Shutdown requested during AP fetch")
            break
            
        query_data = {
            "pageSize": page_size,
            "page": page,
            "sortOrder": "ASC"
        }
        
        try:
            result = ap_module.list(query_data)
            data = result.get('data', [])
            
            # Add venue name to each AP
            for ap in data:
                venue_id = ap.get('venueId', '')
                ap['venueName'] = venues_dict.get(venue_id, 'Unknown')
            
            all_aps.extend(data)
            
            # Check pagination info
            pagination = result.get('pagination', {})
            total_elements = pagination.get('totalElements', 0)
            
            if total_pages is None and total_elements > 0:
                total_pages = (total_elements + page_size - 1) // page_size
                logger.info(f"Total APs to fetch: {total_elements} across {total_pages} pages")
            
            logger.info(f"Fetched page {page + 1}/{total_pages or '?'} - Got {len(data)} APs (Total so far: {len(all_aps)})")
            
            # Check if we have more pages
            if len(data) < page_size:
                break
                
            page += 1
            
        except Exception as e:
            logger.error(f"Error fetching APs on page {page}: {e}")
            # Try to continue with next page
            page += 1
            if page > 100:  # Safety limit
                logger.error("Reached safety limit of 100 pages, stopping")
                break
    
    logger.info(f"Completed fetching APs. Total: {len(all_aps)}")
    return all_aps

def get_all_venues(venues_module: Venues) -> Dict[str, str]:
    """
    Get all venues and return a dictionary mapping venue ID to venue name.
    
    Args:
        venues_module: Venues module instance
        
    Returns:
        Dictionary mapping venue IDs to venue names
    """
    logger.info("Fetching venues...")
    venues_dict = {}
    
    try:
        venues_result = venues_module.list(page_size=100, page=0, sort_order="ASC")
        venues_list = venues_result.get('data', [])
        
        for venue in venues_list:
            venue_id = venue.get('id')
            venue_name = venue.get('name', 'Unknown')
            if venue_id:
                venues_dict[venue_id] = venue_name
        
        logger.info(f"Found {len(venues_dict)} venues")
        
    except Exception as e:
        logger.error(f"Error fetching venues: {e}")
    
    return venues_dict

def export_aps_to_csv(client: RuckusOneClient, output_file: Optional[str] = None) -> str:
    """
    Export all APs to a CSV file.
    
    Args:
        client: RuckusOneClient instance
        output_file: Optional output filename
        
    Returns:
        Path to the created CSV file
    """
    # Initialize modules
    venues_module = Venues(client)
    ap_module = AccessPoints(client)
    
    # Get venues first for name mapping
    venues_dict = get_all_venues(venues_module)
    
    # Get all APs with pagination
    all_aps = get_all_aps(ap_module, venues_dict)
    
    if not all_aps:
        logger.warning("No APs found to export")
        return None
    
    # Generate filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ap_export_{timestamp}.csv"
    
    # Define CSV columns
    fieldnames = [
        'serial_number', 'mac_address', 'model', 'firmware_version',
        'name', 'venue_id', 'venue_name', 'ip_address', 'status'
    ]
    
    # Write to CSV
    logger.info(f"Writing {len(all_aps)} APs to {output_file}...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, ap in enumerate(all_aps):
            if i > 0 and i % 100 == 0:
                logger.debug(f"Written {i}/{len(all_aps)} APs to CSV")
            
            # Extract nested network status info
            network_status = ap.get('networkStatus', {})
            ip_address = network_status.get('ipAddress', '')
            
            row = {
                'serial_number': ap.get('serialNumber', ''),
                'mac_address': ap.get('macAddress', ''),
                'model': ap.get('model', ''),
                'firmware_version': ap.get('firmwareVersion', ''),
                'name': ap.get('name', ''),
                'venue_id': ap.get('venueId', ''),
                'venue_name': ap.get('venueName', ''),
                'ip_address': ip_address,
                'status': ap.get('status', '')
            }
            writer.writerow(row)
    
    logger.info(f"Successfully exported {len(all_aps)} APs to {output_file}")
    return output_file

def load_checkpoint(checkpoint_file: str) -> Dict[str, Any]:
    """Load checkpoint data from file."""
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return {}

def save_checkpoint(checkpoint_file: str, data: Dict[str, Any]):
    """Save checkpoint data to file."""
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save checkpoint: {e}")

def reboot_ap_with_retry(ap_module: AccessPoints, venue_id: str, serial_number: str, 
                         max_retries: int = 3) -> Tuple[bool, str]:
    """
    Reboot an AP with retry logic.
    
    Args:
        ap_module: AccessPoints module instance
        venue_id: Venue ID
        serial_number: AP serial number
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple of (success, error_message)
    """
    for attempt in range(max_retries):
        try:
            result = ap_module.reboot(venue_id, serial_number)
            return True, None
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Reboot failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {error_msg}")
                time.sleep(wait_time)
            else:
                logger.error(f"Reboot failed after {max_retries} attempts: {error_msg}")
                return False, error_msg
    
    return False, "Unknown error"

def import_and_reboot(client: RuckusOneClient, csv_file: str, delay: int = 2,
                     simulate: bool = False, force: bool = False, 
                     resume: bool = False, batch_size: int = 50,
                     skip_status_check: bool = False) -> Dict[str, Any]:
    """
    Import CSV and reboot APs with delay.
    
    Args:
        client: RuckusOneClient instance
        csv_file: Path to CSV file
        delay: Delay in seconds between reboots
        simulate: If True, simulate without actually rebooting
        force: If True, allow rebooting >100 APs
        resume: If True, resume from checkpoint
        batch_size: Number of APs to process before checkpoint
        
    Returns:
        Dictionary with statistics
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    # Initialize modules
    ap_module = AccessPoints(client)
    
    # Read CSV to get AP count
    aps_to_process = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            aps_to_process.append(row)
    
    total_aps = len(aps_to_process)
    
    if total_aps == 0:
        logger.warning("No APs found in CSV file")
        return {'total': 0, 'success': 0, 'failed': 0}
    
    # Safety check
    if total_aps > 100 and not force:
        logger.error(f"CSV contains {total_aps} APs. Use --force flag to reboot more than 100 APs")
        return None
    
    if total_aps > 1000 and not simulate:
        response = input(f"About to reboot {total_aps} APs. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Operation cancelled by user")
            return None
    
    # Checkpoint handling
    checkpoint_file = f".checkpoint_{Path(csv_file).stem}.json"
    checkpoint_data = {}
    start_index = 0
    
    if resume:
        checkpoint_data = load_checkpoint(checkpoint_file)
        start_index = checkpoint_data.get('last_processed_index', 0)
        if start_index > 0:
            logger.info(f"Resuming from AP {start_index + 1}/{total_aps}")
    
    # Calculate estimated time
    estimated_time = (total_aps - start_index) * delay
    estimated_completion = datetime.now() + timedelta(seconds=estimated_time)
    
    mode_str = "SIMULATE MODE" if simulate else "LIVE MODE"
    logger.info(f"{mode_str}: Processing {total_aps - start_index} APs with {delay}s delay")
    logger.info(f"Estimated completion time: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not simulate and not skip_status_check:
        logger.info("Runtime status checking: ENABLED (fetching current status for each AP)")
    elif skip_status_check:
        logger.info("Runtime status checking: DISABLED (trusting CSV status)")
    else:
        logger.info("Runtime status checking: N/A (simulate mode uses CSV status)")
    
    # Statistics
    stats = {
        'total': total_aps,
        'processed': start_index,
        'success': checkpoint_data.get('success', 0),
        'failed': checkpoint_data.get('failed', 0),
        'failed_aps': checkpoint_data.get('failed_aps', [])
    }
    
    # Pre-fetch and cache all APs for status checking (unless skipping or simulating)
    all_aps_cache = {}
    if not simulate and not skip_status_check:
        try:
            logger.info("Pre-fetching all APs for runtime status checking...")
            # Get all APs in one query
            query_data = {
                "pageSize": 1000,
                "page": 0,
                "sortOrder": "ASC"
            }
            result = ap_module.list(query_data)
            all_current_aps = result.get('data', [])
            
            # Cache by serial number for quick lookup
            all_aps_cache = {
                ap.get('serialNumber'): ap for ap in all_current_aps if ap.get('serialNumber')
            }
            logger.info(f"Cached {len(all_aps_cache)} APs for status checking")
            
            # Handle pagination if there are more APs
            pagination = result.get('pagination', {})
            total_pages = pagination.get('totalPages', 1)
            if total_pages > 1:
                logger.info(f"Fetching additional {total_pages - 1} pages of APs...")
                for page in range(1, min(total_pages, 10)):  # Limit to 10 pages max
                    query_data['page'] = page
                    result = ap_module.list(query_data)
                    page_aps = result.get('data', [])
                    for ap in page_aps:
                        if ap.get('serialNumber'):
                            all_aps_cache[ap.get('serialNumber')] = ap
                logger.info(f"Total cached APs: {len(all_aps_cache)}")
        except Exception as e:
            logger.warning(f"Could not pre-fetch APs for status checking: {e}")
            logger.info("Will use CSV status for all APs")
    
    start_time = time.time()
    
    # Process APs
    for i in range(start_index, total_aps):
        if shutdown_requested:
            logger.warning("Shutdown requested, saving checkpoint...")
            checkpoint_data = {
                'last_processed_index': i,
                'success': stats['success'],
                'failed': stats['failed'],
                'failed_aps': stats['failed_aps']
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.info(f"Checkpoint saved. Resume with --resume flag")
            break
        
        ap = aps_to_process[i]
        serial_number = ap.get('serial_number', '')
        venue_id = ap.get('venue_id', '')
        ap_name = ap.get('name', 'Unknown')
        csv_status = ap.get('status', '')  # Status from CSV (potentially outdated)
        
        # Progress indicator with colors
        progress_pct = ((i + 1) / total_aps) * 100
        ap_info = colored(ap_name, 'CYAN', bold=True) + ' (SN: ' + colored(serial_number, 'YELLOW') + ')'
        logger.info(f"[{i + 1}/{total_aps}] ({progress_pct:.1f}%) Processing AP: {ap_info}")
        
        # Get current AP status from pre-fetched cache (unless in simulate mode or skip_status_check is True)
        current_status = csv_status  # Default to CSV status
        if not simulate and not skip_status_check and all_aps_cache:
            if serial_number in all_aps_cache:
                cached_ap = all_aps_cache[serial_number]
                current_status = cached_ap.get('status', csv_status)
                if current_status != csv_status:
                    logger.info(f"  Status update: {colored(csv_status, 'YELLOW')} → {colored(current_status, 'CYAN')}")
            else:
                logger.debug(f"  AP {serial_number} not found in cache, using CSV status: {csv_status}")
        
        # Check if AP is operational (status contains 'Operational' or starts with '2_')
        is_operational = 'Operational' in current_status or current_status.startswith('2_')
        
        if not is_operational:
            skip_msg = f"Skipping AP {colored(ap_name, 'YELLOW')} - Status: {colored(current_status, 'RED')} (not operational)"
            logger.warning(skip_msg)
            if 'skipped_aps' not in stats:
                stats['skipped_aps'] = []
            stats['skipped_aps'].append({
                'serial_number': serial_number,
                'name': ap_name,
                'status': current_status,
                'venue_id': venue_id
            })
            stats['skipped'] = stats.get('skipped', 0) + 1
            continue
        
        if simulate:
            logger.info(f"SIMULATE: Would reboot AP {colored(serial_number, 'YELLOW')} in venue {venue_id}")
            logger.info(f"SIMULATE: API call: PATCH /venues/{venue_id}/aps/{serial_number}/systemCommands with body: {{'type': 'REBOOT'}}")
            stats['success'] += 1
            if 'success_aps' not in stats:
                stats['success_aps'] = []
            stats['success_aps'].append({
                'serial_number': serial_number,
                'name': ap_name,
                'venue_id': venue_id
            })
        else:
            # Actual reboot
            success, error_msg = reboot_ap_with_retry(ap_module, venue_id, serial_number)
            
            if success:
                success_msg = f"Successfully initiated reboot for AP {colored(serial_number, 'GREEN')}"
                logger.info(success_msg)
                stats['success'] += 1
                if 'success_aps' not in stats:
                    stats['success_aps'] = []
                stats['success_aps'].append({
                    'serial_number': serial_number,
                    'name': ap_name,
                    'venue_id': venue_id
                })
            else:
                error_info = f"Failed to reboot AP {colored(serial_number, 'RED')}: {error_msg}"
                logger.error(error_info)
                stats['failed'] += 1
                stats['failed_aps'].append({
                    'serial_number': serial_number,
                    'name': ap_name,
                    'error': error_msg
                })
        
        stats['processed'] += 1
        
        # Save checkpoint periodically
        if (i + 1) % batch_size == 0:
            checkpoint_data = {
                'last_processed_index': i + 1,
                'success': stats['success'],
                'failed': stats['failed'],
                'failed_aps': stats['failed_aps']
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.debug(f"Checkpoint saved at AP {i + 1}")
        
        # Apply delay if not the last AP
        if i < total_aps - 1:
            countdown_with_dots(delay, f"Waiting {delay}s before next AP")
    
    # Clean up checkpoint if completed
    if stats['processed'] == total_aps and os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        logger.info("Operation completed, checkpoint file removed")
    
    # Calculate statistics
    elapsed_time = time.time() - start_time
    avg_time_per_ap = elapsed_time / max(stats['processed'] - start_index, 1)
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info(colored("OPERATION SUMMARY", 'WHITE', bold=True))
    logger.info("=" * 80)
    logger.info(f"Mode: {colored(mode_str, 'CYAN')}")
    logger.info(f"Total APs in CSV: {stats['total']}")
    logger.info(f"APs processed: {stats['processed']}")
    logger.info(f"Successful reboots: {colored(str(stats['success']), 'GREEN')}")
    logger.info(f"Failed reboots: {colored(str(stats['failed']), 'RED' if stats['failed'] > 0 else 'GREEN')}")
    logger.info(f"Skipped (not operational): {colored(str(stats.get('skipped', 0)), 'YELLOW')}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    logger.info(f"Average time per AP: {avg_time_per_ap:.2f} seconds")
    
    # Table of successfully rebooted APs
    if stats.get('success_aps'):
        logger.info("\n" + colored("SUCCESSFULLY REBOOTED APs", 'GREEN', bold=True))
        logger.info("-" * 80)
        logger.info(f"{'AP Name':<30} {'Serial Number':<20} {'Venue ID':<36}")
        logger.info("-" * 80)
        for ap in stats.get('success_aps', []):
            logger.info(f"{ap['name']:<30} {ap['serial_number']:<20} {ap['venue_id']:<36}")
    
    # Table of skipped APs
    if stats.get('skipped_aps'):
        logger.info("\n" + colored("SKIPPED APs (NOT OPERATIONAL)", 'YELLOW', bold=True))
        logger.info("-" * 80)
        logger.info(f"{'AP Name':<25} {'Serial Number':<20} {'Status':<35}")
        logger.info("-" * 80)
        for ap in stats.get('skipped_aps', []):
            status_colored = colored(ap['status'], 'RED')
            logger.info(f"{ap['name']:<25} {ap['serial_number']:<20} {status_colored:<35}")
    
    # Table of failed APs
    if stats.get('failed_aps'):
        logger.info("\n" + colored("FAILED APs", 'RED', bold=True))
        logger.info("-" * 80)
        logger.info(f"{'AP Name':<25} {'Serial Number':<20} {'Error':<35}")
        logger.info("-" * 80)
        for ap in stats.get('failed_aps', []):
            error_short = ap['error'][:35] if len(ap['error']) > 35 else ap['error']
            logger.info(f"{ap['name']:<25} {ap['serial_number']:<20} {error_short:<35}")
    
    return stats

def main():
    """Main function."""
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='RUCKUS One AP Reboot Manager - Export APs to CSV and manage reboots',
        epilog='''
Examples:
  # Export all APs to CSV
  %(prog)s --config config.ini --export
  
  # Export to specific file
  %(prog)s --config config.ini --export --output my_aps.csv
  
  # Simulate reboot (dry run)
  %(prog)s --config config.ini --import my_aps.csv --simulate
  
  # Reboot APs with 2 minute delay between each
  %(prog)s --config config.ini --import my_aps.csv --delay 120 --force
  
  # Skip runtime status check for faster operation
  %(prog)s --config config.ini --import my_aps.csv --skip-status-check
  
  # Resume interrupted operation
  %(prog)s --config config.ini --import my_aps.csv --resume --force

Workflow:
  1. Export APs to CSV: --export
  2. Review CSV and remove unwanted APs
  3. Test with --simulate
  4. Run actual reboot with appropriate --delay
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', required=True, 
                       help='Path to config.ini file with RUCKUS One credentials')
    parser.add_argument('--export', action='store_true', 
                       help='Export all APs to CSV with current status and details')
    parser.add_argument('--import', dest='import_file', 
                       help='Import CSV file and reboot APs listed in it')
    parser.add_argument('--simulate', action='store_true', 
                       help='Simulate mode: show what would be done without actual reboots')
    parser.add_argument('--delay', type=int, default=2, 
                       help='Delay between reboots in seconds (default: 2, shows countdown)')
    parser.add_argument('--output', 
                       help='Custom output filename for export (default: ap_export_YYYYMMDD_HHMMSS.csv)')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging verbosity level (default: INFO)')
    parser.add_argument('--log-file', 
                       help='Write logs to specified file in addition to console')
    parser.add_argument('--force', action='store_true', 
                       help='Required safety flag when rebooting more than 100 APs')
    parser.add_argument('--resume', action='store_true', 
                       help='Resume from last checkpoint after interruption (use with --import)')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Number of APs to process before saving checkpoint (default: 50)')
    parser.add_argument('--skip-status-check', action='store_true',
                       help='Skip runtime status verification and trust CSV status (faster, less safe)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.export and not args.import_file:
        parser.error("Either --export or --import must be specified")
    
    if args.export and args.import_file:
        parser.error("Cannot use --export and --import together")
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize client
        logger.info(f"Initializing RUCKUS One client (region: {config.get('region', 'na')})")
        client = RuckusOneClient(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            tenant_id=config['tenant_id'],
            region=config.get('region', 'na')
        )
        
        # Execute requested operation
        if args.export:
            output_file = export_aps_to_csv(client, args.output)
            if output_file:
                print(f"\nExport completed: {output_file}")
        
        elif args.import_file:
            stats = import_and_reboot(
                client,
                args.import_file,
                delay=args.delay,
                simulate=args.simulate,
                force=args.force,
                resume=args.resume,
                batch_size=args.batch_size,
                skip_status_check=args.skip_status_check
            )
            
            if stats and not shutdown_requested:
                print(f"\nOperation completed successfully")
            elif shutdown_requested:
                print(f"\nOperation interrupted. Use --resume to continue")
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()