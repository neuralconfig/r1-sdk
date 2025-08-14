#!/usr/bin/env python3
"""
RUCKUS One AP CLI Command Manager.

This script provides comprehensive AP CLI command execution capabilities including:
- Export all APs to CSV
- Import CSV files for APs and CLI commands
- Execute CLI commands via SSH with filtering
- Save output to text and CSV formats
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
import paramiko
import threading
import re
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

# Suppress paramiko INFO messages to keep output clean
logging.getLogger("paramiko").setLevel(logging.WARNING)

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

def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a text-based progress bar."""
    if total == 0:
        return "█" * width
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(100 * current / total)
    return f"[{bar}] {percentage}%"

def print_ap_progress(index: int, total: int, ap_info: Dict[str, Any], status: str, 
                     progress_percent: int = 0, final: bool = False):
    """Print a single-line progress update for AP processing."""
    ap_name = ap_info.get('name', 'Unknown')
    venue_name = ap_info.get('venue_name', 'Unknown')
    serial_number = ap_info.get('serial_number', 'Unknown')
    
    # Create progress bar based on percentage
    progress_bar = create_progress_bar(progress_percent, 100, 10)
    
    # Color the status
    if status == "Starting":
        status_colored = colored(status, 'CYAN')
    elif status == "Connecting":
        status_colored = colored(status, 'YELLOW')
    elif status == "Connected":
        status_colored = colored(status, 'GREEN')
    elif status == "Executing":
        status_colored = colored(status, 'BLUE')
    elif status == "Failed":
        status_colored = colored(status, 'RED')
    elif status == "Complete":
        status_colored = colored(status, 'GREEN')
    else:
        status_colored = status
    
    # Format: [1/10] Main Office - Office-AP-01 (SN: 12345) [████████░░] 80% Status
    progress_line = (f"[{index}/{total}] {colored(venue_name, 'CYAN')} - "
                    f"{colored(ap_name, 'WHITE', bold=True)} "
                    f"(SN: {colored(serial_number, 'YELLOW')}) "
                    f"{progress_bar} {status_colored}")
    
    # Pad with spaces to clear any leftover characters (use 120 char width)
    progress_line = progress_line.ljust(120)
    
    # Use \r to overwrite the current line, but only if not in debug mode
    if logger.getEffectiveLevel() > logging.DEBUG:
        print(f"\r{progress_line}", end='', flush=True)
        # If this is the final update for this AP, print newline to move to next line
        if final:
            print()
    else:
        print(progress_line)

def countdown_with_dots(seconds: int, prefix: str = "Waiting"):
    """Show countdown with dots, printing 10s markers."""
    if seconds <= 0:
        return
    
    print(f"{prefix}: ", end='', flush=True)
    
    for i in range(1, seconds + 1):
        if shutdown_requested:
            print(" [Interrupted]")
            break
            
        time.sleep(1)
        
        if i % 10 == 0:
            print(str(i), end='', flush=True)
        else:
            print(".", end='', flush=True)
        
        if i % 50 == 0 and i < seconds:
            print("\n          ", end='', flush=True)
    
    print()

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    if shutdown_requested:
        logger.warning("Force shutdown requested. Exiting immediately...")
        sys.exit(1)
    shutdown_requested = True
    logger.info("Shutdown requested. Press CTRL+C again to force stop...")

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    handlers = [console_handler]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    logging.basicConfig(level=level, handlers=handlers)

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
        'name', 'venue_id', 'venue_name', 'ip_address', 'status', 'ssh_password'
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
                'status': ap.get('status', ''),
                'ssh_password': ''  # Empty, to be filled by user
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


def load_aps_csv(csv_file: str) -> List[Dict[str, Any]]:
    """
    Load AP list from CSV file.
    
    Args:
        csv_file: Path to AP CSV file
        
    Returns:
        List of AP dictionaries
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"AP CSV file not found: {csv_file}")
    
    aps = []
    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = ['serial_number', 'ip_address']
            
            for row_num, row in enumerate(reader, 1):
                # Check for required fields
                missing_fields = [field for field in required_fields if not row.get(field)]
                if missing_fields:
                    logger.warning(f"Row {row_num}: Missing required fields: {missing_fields}")
                    continue
                
                # Skip APs without IP addresses
                if not row['ip_address'] or row['ip_address'].strip() == '':
                    logger.warning(f"Row {row_num}: Skipping AP {row.get('serial_number', 'Unknown')} - no IP address")
                    continue
                
                # Handle optional ssh_password field
                if 'ssh_password' not in row:
                    row['ssh_password'] = ''  # Add empty password if column doesn't exist
                
                aps.append(row)
        
        logger.info(f"Loaded {len(aps)} APs from {csv_file}")
        return aps
        
    except Exception as e:
        logger.error(f"Error reading AP CSV file: {e}")
        raise


def load_commands_csv(csv_file: str) -> List[Dict[str, str]]:
    """
    Load commands from CSV file.
    
    Args:
        csv_file: Path to commands CSV file (format: command,filter)
        
    Returns:
        List of command dictionaries with 'command' and 'filter' keys
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Commands CSV file not found: {csv_file}")
    
    commands = []
    try:
        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            
            for row_num, row in enumerate(reader, 1):
                if not row or len(row) == 0:
                    continue
                
                # Skip header row if it contains 'command'
                if row_num == 1 and len(row) > 0 and 'command' in row[0].lower():
                    continue
                
                command = row[0].strip() if len(row) > 0 else ''
                filter_text = row[1].strip() if len(row) > 1 else ''
                
                if not command:
                    logger.warning(f"Row {row_num}: Empty command, skipping")
                    continue
                
                commands.append({
                    'command': command,
                    'filter': filter_text if filter_text else None
                })
        
        logger.info(f"Loaded {len(commands)} commands from {csv_file}")
        return commands
        
    except Exception as e:
        logger.error(f"Error reading commands CSV file: {e}")
        raise




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


def write_text_output(results: List[Dict[str, Any]], output_file: str):
    """
    Write command results to a text file.
    
    Args:
        results: List of command execution results
        output_file: Path to output text file
    """
    try:
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("AP CLI Command Execution Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for result in results:
                ap_info = result.get('ap_info', {})
                command_results = result.get('command_results', [])
                
                f.write(f"AP: {ap_info.get('name', 'Unknown')} (SN: {ap_info.get('serial_number', 'Unknown')})\n")
                f.write(f"IP: {ap_info.get('ip_address', 'Unknown')}\n")
                f.write(f"Venue: {ap_info.get('venue_name', 'Unknown')}\n")
                f.write("-"*60 + "\n")
                
                for cmd_result in command_results:
                    f.write(f"\nCommand: {cmd_result.get('command', 'Unknown')}\n")
                    if cmd_result.get('filter'):
                        f.write(f"Filter: {cmd_result.get('filter')}\n")
                    f.write(f"Timestamp: {cmd_result.get('timestamp', 'Unknown')}\n")
                    
                    if cmd_result.get('error'):
                        f.write(f"ERROR: {cmd_result.get('error')}\n")
                    else:
                        output_to_show = cmd_result.get('filtered_output', cmd_result.get('output', ''))
                        f.write(f"Output:\n{output_to_show}\n")
                    f.write("-"*40 + "\n")
                
                f.write("\n" + "="*80 + "\n\n")
        
        logger.info(f"Text output written to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to write text output: {e}")


def write_success_csv(successful_aps: List[Dict[str, Any]], output_file: str):
    """
    Write successful APs to CSV file.
    
    Args:
        successful_aps: List of successful AP dictionaries
        output_file: Path to output CSV file
    """
    try:
        if not successful_aps:
            logger.warning("No successful APs to export")
            return
            
        with open(output_file, 'w', newline='') as csvfile:
            # Use original AP fields plus execution results
            fieldnames = list(successful_aps[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for ap in successful_aps:
                writer.writerow(ap)
        
        logger.info(f"Success CSV written to {output_file} ({len(successful_aps)} APs)")
        
    except Exception as e:
        logger.error(f"Failed to write success CSV: {e}")


def write_failed_csv(failed_aps: List[Dict[str, Any]], output_file: str):
    """
    Write failed APs to CSV file.
    
    Args:
        failed_aps: List of failed AP dictionaries
        output_file: Path to output CSV file
    """
    try:
        if not failed_aps:
            logger.warning("No failed APs to export")
            return
            
        with open(output_file, 'w', newline='') as csvfile:
            # Use original AP fields plus failure information
            fieldnames = list(failed_aps[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for ap in failed_aps:
                writer.writerow(ap)
        
        logger.info(f"Failed CSV written to {output_file} ({len(failed_aps)} APs)")
        
    except Exception as e:
        logger.error(f"Failed to write failed CSV: {e}")


def write_csv_output(results: List[Dict[str, Any]], output_file: str):
    """
    Write command results to a CSV file.
    
    Args:
        results: List of command execution results
        output_file: Path to output CSV file
    """
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['ap_serial', 'ap_name', 'ap_ip', 'command', 'filter', 'output', 'error', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                ap_info = result.get('ap_info', {})
                command_results = result.get('command_results', [])
                
                for cmd_result in command_results:
                    output_to_save = cmd_result.get('filtered_output', cmd_result.get('output', ''))
                    # Clean output for CSV (remove newlines, limit length)
                    if output_to_save:
                        output_to_save = output_to_save.replace('\n', ' | ').replace('\r', '')
                        if len(output_to_save) > 1000:  # Limit output length
                            output_to_save = output_to_save[:1000] + "... [truncated]"
                    
                    row = {
                        'ap_serial': ap_info.get('serial_number', ''),
                        'ap_name': ap_info.get('name', ''),
                        'ap_ip': ap_info.get('ip_address', ''),
                        'command': cmd_result.get('command', ''),
                        'filter': cmd_result.get('filter', ''),
                        'output': output_to_save,
                        'error': cmd_result.get('error', ''),
                        'timestamp': cmd_result.get('timestamp', '')
                    }
                    writer.writerow(row)
        
        logger.info(f"CSV output written to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to write CSV output: {e}")


def execute_commands_on_aps(
    ap_list: List[Dict[str, Any]], 
    commands: List[Dict[str, str]], 
    default_password: str,
    simulate: bool = False,
    delay: int = 2,
    timeout: int = 30,
    force: bool = False,
    resume: bool = False,
    batch_size: int = 50,
    ssh_retries: int = 2,
    include_non_operational: bool = False
) -> Dict[str, Any]:
    """
    Execute commands on a list of APs.
    
    Args:
        ap_list: List of AP dictionaries
        commands: List of command dictionaries
        default_password: Default SSH password (fallback if not in CSV)
        simulate: If True, simulate without executing
        delay: Delay between operations
        timeout: SSH timeout
        force: Allow processing >100 APs
        resume: Resume from checkpoint
        batch_size: Operations before checkpoint
        ssh_retries: Number of SSH connection attempts
        include_non_operational: Whether to try non-operational APs
        
    Returns:
        Dictionary with execution results and statistics
    """
    total_aps = len(ap_list)
    total_commands = len(commands)
    total_operations = total_aps * total_commands
    
    if total_aps == 0:
        logger.warning("No APs to process")
        return {'results': [], 'successful_aps': [], 'failed_aps': []}
    
    if total_commands == 0:
        logger.warning("No commands to execute")
        return {'results': [], 'successful_aps': [], 'failed_aps': []}
    
    # Sort APs by priority: operational first, then non-operational
    def is_operational(ap):
        status = ap.get('status', '')
        return 'Operational' in status or status.startswith('2_')
    
    operational_aps = [ap for ap in ap_list if is_operational(ap)]
    non_operational_aps = [ap for ap in ap_list if not is_operational(ap)]
    
    # Build processing list based on flags
    if include_non_operational:
        aps_to_process = operational_aps + non_operational_aps
        logger.info(f"Processing {len(operational_aps)} operational + {len(non_operational_aps)} non-operational APs")
    else:
        aps_to_process = operational_aps
        logger.info(f"Processing {len(operational_aps)} operational APs (skipping {len(non_operational_aps)} non-operational)")
    
    # Update totals
    total_aps = len(aps_to_process)
    total_operations = total_aps * total_commands
    
    # Safety checks
    if total_aps > 100 and not force:
        logger.error(f"Processing {total_aps} APs. Use --force flag to process more than 100 APs")
        return {'results': [], 'successful_aps': [], 'failed_aps': []}
    
    if total_operations > 1000 and not simulate:
        response = input(f"About to execute {total_operations} operations ({total_aps} APs × {total_commands} commands). Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Operation cancelled by user")
            return {'results': [], 'successful_aps': [], 'failed_aps': []}
    
    # Checkpoint handling
    checkpoint_file = f".checkpoint_ap_cli_{int(time.time())}.json"
    checkpoint_data = {}
    start_ap_index = 0
    
    if resume:
        # Look for existing checkpoint files
        checkpoint_files = [f for f in os.listdir('.') if f.startswith('.checkpoint_ap_cli_')]
        if checkpoint_files:
            checkpoint_file = checkpoint_files[-1]  # Use the most recent
            checkpoint_data = load_checkpoint(checkpoint_file)
            start_ap_index = checkpoint_data.get('last_processed_ap_index', 0)
            if start_ap_index > 0:
                logger.info(f"Resuming from AP {start_ap_index + 1}/{total_aps}")
    
    # Calculate estimated time
    estimated_time = (total_aps - start_ap_index) * total_commands * (delay + 5)  # 5s estimated per command
    estimated_completion = datetime.now() + timedelta(seconds=estimated_time)
    
    mode_str = "SIMULATE MODE" if simulate else "LIVE MODE"
    logger.info(f"{mode_str}: Processing {total_aps - start_ap_index} APs with {total_commands} commands each")
    logger.info(f"Estimated completion time: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = checkpoint_data.get('results', [])
    successful_aps = checkpoint_data.get('successful_aps', [])
    failed_aps = checkpoint_data.get('failed_aps', [])
    stats = {
        'total_aps': total_aps,
        'processed_aps': start_ap_index,
        'successful_connections': checkpoint_data.get('successful_connections', 0),
        'failed_connections': checkpoint_data.get('failed_connections', 0),
        'total_commands_executed': checkpoint_data.get('total_commands_executed', 0),
        'total_commands_failed': checkpoint_data.get('total_commands_failed', 0)
    }
    
    start_time = time.time()
    
    # Process APs
    for i in range(start_ap_index, total_aps):
        if shutdown_requested:
            logger.warning("Shutdown requested, saving checkpoint...")
            checkpoint_data = {
                'last_processed_ap_index': i,
                'results': results,
                'successful_aps': successful_aps,
                'failed_aps': failed_aps,
                'successful_connections': stats['successful_connections'],
                'failed_connections': stats['failed_connections'],
                'total_commands_executed': stats['total_commands_executed'],
                'total_commands_failed': stats['total_commands_failed']
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.info(f"Checkpoint saved. Resume with --resume flag")
            break
        
        ap = aps_to_process[i]  # Use the prioritized list
        ap_serial = ap.get('serial_number', 'Unknown')
        ap_name = ap.get('name', 'Unknown')
        ap_ip = ap.get('ip_address', '')
        
        # Determine password to use for this AP
        ap_password = ap.get('ssh_password', '').strip()
        if not ap_password:
            ap_password = default_password
        
        # Show starting progress
        print_ap_progress(i + 1, total_aps, ap, "Starting", 0)
        
        # Debug logging only
        if logger.getEffectiveLevel() <= logging.DEBUG:
            password_source = "CSV" if ap.get('ssh_password', '').strip() else "default"
            logger.debug(f"Processing AP {ap_serial} using {password_source} password")
        
        ap_result = {
            'ap_info': ap,
            'command_results': []
        }
        
        if simulate:
            print_ap_progress(i + 1, total_aps, ap, "Connecting", 25)
            time.sleep(0.5)  # Small delay to show progress
            print_ap_progress(i + 1, total_aps, ap, "Connected", 50)
            if logger.getEffectiveLevel() <= logging.DEBUG:
                password_source = "CSV" if ap.get('ssh_password', '').strip() else "default"
                logger.debug(f"SIMULATE: Would connect to AP {ap_ip} with SSH (user: admin, password: {'from CSV' if password_source == 'CSV' else 'default'})")
            
            for cmd_idx, cmd in enumerate(commands):
                # Calculate progress: 50% base + (command progress * 40%)
                cmd_progress = 50 + int((cmd_idx + 1) / len(commands) * 40)
                print_ap_progress(i + 1, total_aps, ap, "Executing", cmd_progress)
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.debug(f"SIMULATE: Would execute command '{cmd['command']}' with filter '{cmd.get('filter', 'none')}'")
                ap_result['command_results'].append({
                    'command': cmd['command'],
                    'filter': cmd.get('filter'),
                    'output': f"SIMULATED OUTPUT for command: {cmd['command']}",
                    'filtered_output': f"SIMULATED FILTERED OUTPUT for command: {cmd['command']}",
                    'timestamp': datetime.now().isoformat()
                })
                stats['total_commands_executed'] += 1
                time.sleep(0.3)  # Small delay to show progress
            stats['successful_connections'] += 1
            print_ap_progress(i + 1, total_aps, ap, "Complete", 100, final=True)
            
        else:
            # Actual SSH connection and command execution
            print_ap_progress(i + 1, total_aps, ap, "Connecting", 25)
            ssh_conn = APSSHConnection(ap_ip, "admin", ap_password, timeout)
            
            # Try to connect with retry logic
            connection_success, attempts_made, connection_error = ssh_conn.connect_with_retry(ssh_retries)
            
            if connection_success:
                print_ap_progress(i + 1, total_aps, ap, "Connected", 50)
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.debug(f"Successfully connected to AP {ap_serial} (attempt {attempts_made})")
                stats['successful_connections'] += 1
                
                # Execute each command
                commands_successful = 0
                commands_failed = 0
                for cmd_idx, cmd in enumerate(commands):
                    # Calculate progress: 50% base + (command progress * 40%)
                    cmd_progress = 50 + int((cmd_idx + 1) / len(commands) * 40)
                    print_ap_progress(i + 1, total_aps, ap, "Executing", cmd_progress)
                    cmd_result = ssh_conn.execute_command(cmd['command'], cmd.get('filter'))
                    ap_result['command_results'].append(cmd_result)
                    
                    if cmd_result.get('error'):
                        if logger.getEffectiveLevel() <= logging.DEBUG:
                            logger.debug(f"Command '{cmd['command']}' failed: {cmd_result['error']}")
                        stats['total_commands_failed'] += 1
                        commands_failed += 1
                    else:
                        if logger.getEffectiveLevel() <= logging.DEBUG:
                            logger.debug(f"Command '{cmd['command']}' executed successfully")
                        stats['total_commands_executed'] += 1
                        commands_successful += 1
                    
                    # Small delay between commands on same AP
                    if len(commands) > 1:
                        time.sleep(1)
                
                ssh_conn.cleanup()
                print_ap_progress(i + 1, total_aps, ap, "Complete", 100, final=True)
                
                # Add to successful APs list
                ap_success_info = dict(ap)
                ap_success_info.update({
                    'commands_executed': commands_successful,
                    'commands_failed': commands_failed,
                    'execution_time': datetime.now().isoformat(),
                    'ssh_attempts': attempts_made
                })
                successful_aps.append(ap_success_info)
                
            else:
                print_ap_progress(i + 1, total_aps, ap, "Failed", 0, final=True)
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    logger.debug(f"Failed to connect to AP {ap_serial} at {ap_ip} after {attempts_made} attempts: {connection_error}")
                stats['failed_connections'] += 1
                
                # Add error entries for all commands
                for cmd in commands:
                    ap_result['command_results'].append({
                        'command': cmd['command'],
                        'filter': cmd.get('filter'),
                        'error': f"Failed to connect to AP {ap_ip}: {connection_error}",
                        'output': '',
                        'filtered_output': '',
                        'timestamp': datetime.now().isoformat()
                    })
                    stats['total_commands_failed'] += 1
                
                # Add to failed APs list
                ap_failure_info = dict(ap)
                ap_failure_info.update({
                    'failure_reason': 'Connection failed',
                    'error_details': connection_error,
                    'ssh_attempts': attempts_made,
                    'failure_time': datetime.now().isoformat()
                })
                failed_aps.append(ap_failure_info)
        
        results.append(ap_result)
        stats['processed_aps'] += 1
        
        # Save checkpoint periodically
        if (i + 1) % batch_size == 0:
            checkpoint_data = {
                'last_processed_ap_index': i + 1,
                'results': results,
                'successful_aps': successful_aps,
                'failed_aps': failed_aps,
                'successful_connections': stats['successful_connections'],
                'failed_connections': stats['failed_connections'],
                'total_commands_executed': stats['total_commands_executed'],
                'total_commands_failed': stats['total_commands_failed']
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.debug(f"Checkpoint saved at AP {i + 1}")
        
        # Apply delay if not the last AP
        if i < total_aps - 1 and delay > 0:
            countdown_with_dots(delay, f"Waiting {delay}s before next AP")
    
    # Clean up checkpoint if completed
    if stats['processed_aps'] == total_aps and os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        logger.info("Operation completed, checkpoint file removed")
    
    # No need for final newline - each AP already printed its own line
    
    # Print summary
    elapsed_time = time.time() - start_time
    logger.info("\n" + "="*80)
    logger.info(colored("OPERATION SUMMARY", 'WHITE', bold=True))
    logger.info("="*80)
    logger.info(f"Mode: {colored(mode_str, 'CYAN')}")
    logger.info(f"Total APs: {stats['total_aps']}")
    logger.info(f"APs processed: {stats['processed_aps']}")
    logger.info(f"Successful connections: {colored(str(stats['successful_connections']), 'GREEN')}")
    logger.info(f"Failed connections: {colored(str(stats['failed_connections']), 'RED' if stats['failed_connections'] > 0 else 'GREEN')}")
    logger.info(f"Commands executed: {colored(str(stats['total_commands_executed']), 'GREEN')}")
    logger.info(f"Commands failed: {colored(str(stats['total_commands_failed']), 'RED' if stats['total_commands_failed'] > 0 else 'GREEN')}")
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    
    return {
        'results': results,
        'successful_aps': successful_aps,
        'failed_aps': failed_aps,
        'stats': stats
    }


def generate_comprehensive_report(results: List[Dict[str, Any]], stats: Dict[str, Any], 
                                commands: List[Dict[str, str]], text_output_file: Optional[str] = None) -> str:
    """
    Generate a comprehensive report with statistics and output analysis.
    
    Args:
        results: List of command execution results
        stats: Execution statistics
        commands: List of commands that were executed
        text_output_file: Optional text file to append the report to
        
    Returns:
        Report string
    """
    report_lines = []
    
    # Header
    report_lines.append("\n" + "="*80)
    report_lines.append("COMPREHENSIVE ANALYSIS REPORT")
    report_lines.append("="*80)
    
    # Success percentage statistics
    total_aps = stats['total_aps']
    successful_connections = stats['successful_connections']
    successful_percentage = (successful_connections / total_aps * 100) if total_aps > 0 else 0
    
    report_lines.append(f"\nCONNECTION STATISTICS:")
    report_lines.append(f"   * Total APs processed: {total_aps}")
    report_lines.append(f"   * Successful connections: {successful_connections} ({successful_percentage:.1f}%)")
    report_lines.append(f"   * Failed connections: {stats['failed_connections']} ({100-successful_percentage:.1f}%)")
    
    # Command execution statistics
    total_commands_attempted = stats['total_commands_executed'] + stats['total_commands_failed']
    command_success_percentage = (stats['total_commands_executed'] / total_commands_attempted * 100) if total_commands_attempted > 0 else 0
    
    report_lines.append(f"\nCOMMAND EXECUTION STATISTICS:")
    report_lines.append(f"   * Total commands attempted: {total_commands_attempted}")
    report_lines.append(f"   * Successful commands: {stats['total_commands_executed']} ({command_success_percentage:.1f}%)")
    report_lines.append(f"   * Failed commands: {stats['total_commands_failed']} ({100-command_success_percentage:.1f}%)")
    
    # Analyze command outputs for each command
    for cmd in commands:
        command_name = cmd['command']
        filter_text = cmd.get('filter', '')
        
        report_lines.append(f"\nANALYSIS FOR COMMAND: '{command_name}'")
        if filter_text:
            report_lines.append(f"   Filter: '{filter_text}'")
        
        # Collect all outputs for this command
        command_outputs = {}  # output -> [list of APs that had this output]
        
        for result in results:
            ap_info = result.get('ap_info', {})
            ap_name = ap_info.get('name', 'Unknown')
            for cmd_result in result.get('command_results', []):
                if cmd_result.get('command') == command_name:
                    if cmd_result.get('error'):
                        output_key = f"ERROR: {cmd_result['error']}"
                    else:
                        # Use filtered output if available, otherwise raw output
                        output = cmd_result.get('filtered_output', cmd_result.get('output', ''))
                        if not output.strip():
                            output_key = "[No output]"
                        else:
                            # Truncate long outputs for grouping
                            output_key = output.strip()[:200]
                            if len(output.strip()) > 200:
                                output_key += "... [truncated]"
                    
                    if output_key not in command_outputs:
                        command_outputs[output_key] = []
                    command_outputs[output_key].append(ap_name)
        
        # Sort by frequency (most common first)
        sorted_outputs = sorted(command_outputs.items(), key=lambda x: len(x[1]), reverse=True)
        
        if not sorted_outputs:
            report_lines.append("   WARNING: No results found for this command")
            continue
        
        report_lines.append(f"   Found {len(sorted_outputs)} unique response patterns:")
        
        for i, (output, ap_list) in enumerate(sorted_outputs[:10], 1):  # Show top 10 patterns
            percentage = len(ap_list) / len([r for r in results if any(cr.get('command') == command_name for cr in r.get('command_results', []))]) * 100
            report_lines.append(f"\n   {i}. Response pattern ({len(ap_list)} APs, {percentage:.1f}%):")
            
            # Show first few lines of output
            output_preview = output.split('\n')[0] if output else "[Empty]"
            if len(output_preview) > 80:
                output_preview = output_preview[:80] + "..."
            report_lines.append(f"      Preview: {output_preview}")
            
            # Show AP names (limit to first 5)
            ap_names_str = ", ".join(ap_list[:5])
            if len(ap_list) > 5:
                ap_names_str += f" ... and {len(ap_list) - 5} more"
            report_lines.append(f"      APs: {ap_names_str}")
        
        if len(sorted_outputs) > 10:
            report_lines.append(f"   ... and {len(sorted_outputs) - 10} more response patterns")
    
    report_lines.append("\n" + "="*80)
    
    # Join all lines
    report_text = "\n".join(report_lines)
    
    # Print to console
    print(report_text)
    
    # Append to text file if specified
    if text_output_file:
        try:
            with open(text_output_file, 'a') as f:
                f.write(report_text + "\n")
            logger.info(f"Comprehensive report appended to {text_output_file}")
        except Exception as e:
            logger.error(f"Failed to append report to {text_output_file}: {e}")
    
    return report_text


class APSSHConnection:
    """SSH connection handler for AP CLI commands."""
    
    def __init__(self, ap_ip: str, username: str, password: str, timeout: int = 30):
        """
        Initialize SSH connection to AP.
        
        Args:
            ap_ip: IP address of the AP
            username: SSH username
            password: SSH password
            timeout: Connection timeout in seconds
        """
        self.ap_ip = ap_ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None
        self.shell = None
        self.connected = False
        self.connection_lock = threading.Lock()
        self.last_error = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection to AP.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.connection_lock:
                logger.debug(f"Connecting to AP at {self.ap_ip}")
                
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # RUCKUS APs expect no initial authentication - they prompt interactively
                try:
                    # Connect with no authentication - let AP handle prompts
                    transport = paramiko.Transport((self.ap_ip, 22))
                    transport.connect()
                    
                    try:
                        # Try none authentication first (what RUCKUS APs expect)
                        transport.auth_none("")
                        logger.debug("None auth successful")
                    except:
                        logger.debug("None auth failed, but continuing...")
                    
                    # Create client from transport
                    self.client = paramiko.SSHClient()
                    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self.client._transport = transport
                    
                except Exception as e:
                    logger.debug(f"Transport connection failed: {e}")
                    # Fallback to traditional connection
                    try:
                        self.client.connect(
                            hostname=self.ap_ip,
                            port=22,
                            username="",  # Empty username - let AP prompt
                            password="",  # Empty password - let AP prompt
                            timeout=15,
                            allow_agent=False,
                            look_for_keys=False
                        )
                        logger.debug("Connected with empty credentials")
                    except Exception as e2:
                        logger.debug(f"All connection methods failed: {e2}")
                        raise
                
                # Open shell for interactive commands
                self.shell = self.client.invoke_shell()
                self.shell.settimeout(self.timeout)
                
                # Handle login prompts if needed
                if self._handle_login_prompts():
                    self.connected = True
                    logger.debug(f"Successfully connected to AP {self.ap_ip}")
                    return True
                else:
                    logger.error(f"Failed to authenticate to AP {self.ap_ip}")
                    self.cleanup()
                    return False
                    
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Connection failed to AP {self.ap_ip}: {e}")
            self.cleanup()
            return False
    
    def connect_with_retry(self, max_retries: int = 2) -> Tuple[bool, int, str]:
        """
        Establish SSH connection with retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts
            
        Returns:
            Tuple of (success, attempts_made, error_message)
        """
        for attempt in range(1, max_retries + 1):
            logger.debug(f"SSH connection attempt {attempt}/{max_retries} to {self.ap_ip}")
            
            if self.connect():
                return True, attempt, None
            
            if attempt < max_retries:
                wait_time = min(2 ** (attempt - 1), 10)  # Exponential backoff, max 10s
                logger.warning(f"Connection attempt {attempt} failed to {self.ap_ip}, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} connection attempts failed to {self.ap_ip}")
        
        return False, max_retries, self.last_error or "Connection failed"
    
    def _handle_login_prompts(self) -> bool:
        """Handle interactive login prompts."""
        logger.debug("Handling RUCKUS login prompts")
        
        # Wait for initial output
        time.sleep(2)
        
        # Read any initial output
        output = ""
        while self.shell.recv_ready():
            output += self.shell.recv(1024).decode('utf-8', errors='ignore')
            
        logger.debug(f"Initial output: {repr(output[:100])}")
        
        # Handle login prompts
        max_attempts = 15
        username_sent = False
        password_sent = False
        
        for attempt in range(max_attempts):
            if "Please login:" in output and not username_sent:
                logger.debug(f"Sending username (attempt {attempt + 1})")
                self.shell.send(f"{self.username}\n")
                username_sent = True
                time.sleep(1)
                
            elif "password :" in output and not password_sent:
                logger.debug(f"Sending password (attempt {attempt + 1})")
                self.shell.send(f"{self.password}\n")
                password_sent = True
                time.sleep(2)
                
            elif "rkscli:" in output:
                logger.debug("Reached RUCKUS CLI prompt")
                return True
                
            elif "Invalid" in output or "denied" in output.lower():
                logger.debug("Authentication failed")
                return False
                
            # Read more output
            time.sleep(1)
            new_output = ""
            while self.shell.recv_ready():
                chunk = self.shell.recv(1024).decode('utf-8', errors='ignore')
                new_output += chunk
                
            if new_output:
                output += new_output
                logger.debug(f"Additional output: {repr(new_output[:50])}")
            
        logger.debug("Login timeout - did not reach CLI prompt")
        return False
    
    def execute_command(self, command: str, filter_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute command on AP.
        
        Args:
            command: Command to execute
            filter_text: Optional filter to apply to output (like grep)
            
        Returns:
            Dictionary with command output and metadata
        """
        if not self.connected or not self.shell:
            return {"error": "Not connected", "output": "", "filtered_output": ""}
        
        try:
            with self.connection_lock:
                # Clear any pending output
                while self.shell.recv_ready():
                    self.shell.recv(1024)
                
                # Send command
                self.shell.send(f"{command}\n")
                time.sleep(1)
                
                # Collect response
                output = ""
                timeout_count = 0
                max_timeout = 20
                
                while timeout_count < max_timeout:
                    if self.shell.recv_ready():
                        chunk = self.shell.recv(4096).decode('utf-8', errors='ignore')
                        output += chunk
                        timeout_count = 0
                        
                        # Check if we got the prompt back
                        if any(prompt in chunk for prompt in ["rkscli:", "#", "$", ">"]):
                            break
                    else:
                        time.sleep(0.5)
                        timeout_count += 1
                
                # Apply filter if specified
                filtered_output = output
                if filter_text:
                    filtered_lines = []
                    for line in output.split('\n'):
                        if filter_text.lower() in line.lower():
                            filtered_lines.append(line)
                    filtered_output = '\n'.join(filtered_lines)
                
                return {
                    "output": output,
                    "filtered_output": filtered_output,
                    "timestamp": datetime.now().isoformat(),
                    "command": command,
                    "filter": filter_text
                }
                
        except Exception as e:
            logger.error(f"Command execution failed on AP {self.ap_ip}: {e}")
            return {"error": str(e), "output": "", "filtered_output": ""}
    
    def cleanup(self):
        """Clean up SSH connection."""
        with self.connection_lock:
            self.connected = False
            if self.shell:
                try:
                    self.shell.close()
                except:
                    pass
            if self.client:
                try:
                    self.client.close()
                except:
                    pass


def main():
    """Main function."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='RUCKUS One AP CLI Command Manager - Execute CLI commands on APs',
        epilog='''
Examples:
  # Export all APs to CSV
  %(prog)s --config config.ini --export
  
  # Execute commands on APs
  %(prog)s --config config.ini --import-aps aps.csv --import-commands commands.csv --password secret
  
  # Simulate command execution (dry run)
  %(prog)s --config config.ini --import-aps aps.csv --import-commands commands.csv --password secret --simulate
  
  # Save output to files
  %(prog)s --config config.ini --import-aps aps.csv --import-commands commands.csv --password secret --output-text results.txt --output-csv results.csv
  
  # Include non-operational APs and export success/failure lists
  %(prog)s --config config.ini --import-aps aps.csv --import-commands commands.csv --password secret --include-non-operational --export-success-csv success.csv --export-failed-csv failed.csv
  
  # Use custom SSH retry count
  %(prog)s --config config.ini --import-aps aps.csv --import-commands commands.csv --password secret --ssh-retries 3

Commands CSV format:
  command,filter
  show version,
  show vxlan status,vxlan
  get wlaninfo,enabled
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', required=True,
                       help='Path to config.ini file with RUCKUS One credentials')
    parser.add_argument('--export', action='store_true',
                       help='Export all APs to CSV')
    parser.add_argument('--import-aps',
                       help='Import AP list CSV file')
    parser.add_argument('--import-commands',
                       help='Import commands CSV file (format: command,filter)')
    parser.add_argument('--password', required=False,
                       help='Default SSH password for operational APs without passwords in CSV (username is always "admin")')
    parser.add_argument('--simulate', action='store_true',
                       help='Simulate mode: show what would be done without executing')
    parser.add_argument('--delay', type=int, default=0,
                       help='Delay between operations in seconds (default: 0)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='SSH connection timeout in seconds (default: 30)')
    parser.add_argument('--output-text',
                       help='Save output to text file')
    parser.add_argument('--output-csv',
                       help='Save output to CSV file (format: AP Serial,command,output)')
    parser.add_argument('--output',
                       help='Custom output filename for export')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging verbosity level')
    parser.add_argument('--log-file',
                       help='Write logs to specified file')
    parser.add_argument('--force', action='store_true',
                       help='Required safety flag when processing more than 100 APs')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last checkpoint')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Number of operations before saving checkpoint')
    parser.add_argument('--ssh-retries', type=int, default=2,
                       help='Number of SSH connection attempts per AP (default: 2)')
    parser.add_argument('--include-non-operational', action='store_true',
                       help='Also attempt to connect to non-operational APs')
    parser.add_argument('--export-success-csv',
                       help='Export successful APs to CSV file')
    parser.add_argument('--export-failed-csv',
                       help='Export failed APs to CSV file')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.export and not (args.import_aps and args.import_commands):
        parser.error("Either --export or both --import-aps and --import-commands must be specified")
    
    if args.export and (args.import_aps or args.import_commands):
        parser.error("Cannot use --export with --import options")
    
    # Password validation will be done after loading CSV to check if passwords are present
    
    setup_logging(args.log_level, args.log_file)
    
    try:
        config = load_config(args.config)
        
        logger.info(f"Initializing RUCKUS One client (region: {config.get('region', 'na')})")
        client = RuckusOneClient(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            tenant_id=config['tenant_id'],
            region=config.get('region', 'na')
        )
        
        if args.export:
            output_file = export_aps_to_csv(client, args.output)
            if output_file:
                print(f"\nExport completed: {output_file}")
            
        else:
            # Load APs and commands from CSV files
            try:
                ap_list = load_aps_csv(args.import_aps)
                commands = load_commands_csv(args.import_commands)
                
                # Check if we need a fallback password (only for operational APs)
                operational_aps = [ap for ap in ap_list if 'Operational' in ap.get('status', '') or ap.get('status', '').startswith('2_')]
                operational_aps_without_passwords = [ap for ap in operational_aps if not ap.get('ssh_password', '').strip()]
                
                if operational_aps_without_passwords and not args.password:
                    logger.error(f"Found {len(operational_aps_without_passwords)} operational APs without passwords in CSV, but no --password provided as fallback")
                    logger.error("Either add passwords to all operational APs in the CSV or provide --password argument")
                    sys.exit(1)
                
                logger.info(f"Loaded {len(ap_list)} APs total, {len(operational_aps)} operational, {len(operational_aps_without_passwords)} operational without CSV passwords")
                
                # Execute commands
                execution_result = execute_commands_on_aps(
                    ap_list=ap_list,
                    commands=commands,
                    default_password=args.password,
                    simulate=args.simulate,
                    delay=args.delay,
                    timeout=args.timeout,
                    force=args.force,
                    resume=args.resume,
                    batch_size=args.batch_size,
                    ssh_retries=args.ssh_retries,
                    include_non_operational=args.include_non_operational
                )
                
                results = execution_result['results']
                successful_aps = execution_result['successful_aps']
                failed_aps = execution_result['failed_aps']
                stats = execution_result['stats']
                
                # Write output files if specified
                if args.output_text and results:
                    write_text_output(results, args.output_text)
                    print(f"\nText output written to: {args.output_text}")
                
                if args.output_csv and results:
                    write_csv_output(results, args.output_csv)
                    print(f"\nCSV output written to: {args.output_csv}")
                
                if args.export_success_csv and successful_aps:
                    write_success_csv(successful_aps, args.export_success_csv)
                    print(f"\nSuccess CSV written to: {args.export_success_csv}")
                
                if args.export_failed_csv and failed_aps:
                    write_failed_csv(failed_aps, args.export_failed_csv)
                    print(f"\nFailed CSV written to: {args.export_failed_csv}")
                
                # Generate comprehensive report if there are results
                if results:
                    generate_comprehensive_report(results, stats, commands, args.output_text)
                    print(f"\nCommand execution completed successfully")
                    print(f"Summary: {len(successful_aps)} successful, {len(failed_aps)} failed")
                    
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error during command execution: {e}")
                sys.exit(1)
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()