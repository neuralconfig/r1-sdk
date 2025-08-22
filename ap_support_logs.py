#!/usr/bin/env python3
"""
RUCKUS One AP Support Log Downloader and Analyzer.

This script provides comprehensive AP support log management capabilities including:
- Export all APs to CSV
- Import CSV files for AP selection
- Download AP support logs via API
- Analyze logs with customizable search patterns
- Parallel processing for multiple APs
- Generate reports with good/bad configuration analysis
- Resume capability for interrupted operations
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
import gzip
import shutil
import threading
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.venues import Venues
from ruckus_one.modules.access_points import AccessPoints

# Configure logging
logger = logging.getLogger(__name__)

# Suppress urllib3 warnings for cleaner output
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def display_overall_progress(completed: int, total: int, good: int, bad: int, unknown: int, failed: int, show_progress: bool = False):
    """Display overall progress with statistics."""
    if not show_progress:
        return
    
    progress_bar = create_progress_bar(completed, total, 10)
    percentage = int(100 * completed / total) if total > 0 else 0
    
    progress_line = (f"Overall: {progress_bar} | "
                    f"Processed: {colored(str(completed), 'WHITE')}/{total} | "
                    f"Good: {colored(str(good), 'GREEN')} | "
                    f"Bad: {colored(str(bad), 'RED')} | "
                    f"Unknown: {colored(str(unknown), 'YELLOW')} | "
                    f"Failed: {colored(str(failed), 'RED')}")
    
    # Use carriage return to overwrite the line, pad with spaces to clear any leftover characters
    print(f"\r{progress_line.ljust(120)}", end='', flush=True)

def print_progress(index: int, total: int, ap_info: Dict[str, Any], status: str, 
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
    elif status == "Requesting":
        status_colored = colored(status, 'YELLOW')
    elif status == "Waiting":
        status_colored = colored(status, 'BLUE')
    elif status == "Downloading":
        status_colored = colored(status, 'MAGENTA')
    elif status == "Analyzing":
        status_colored = colored(status, 'BLUE')
    elif status == "Complete":
        status_colored = colored(status, 'GREEN')
    elif status == "Failed":
        status_colored = colored(status, 'RED')
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
            required_fields = ['serial_number']
            
            for row_num, row in enumerate(reader, 1):
                # Check for required fields
                missing_fields = [field for field in required_fields if not row.get(field)]
                if missing_fields:
                    logger.warning(f"Row {row_num}: Missing required fields: {missing_fields}")
                    continue
                
                aps.append(row)
        
        logger.info(f"Loaded {len(aps)} APs from {csv_file}")
        return aps
        
    except Exception as e:
        logger.error(f"Error reading AP CSV file: {e}")
        raise

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

class APLogDownloader:
    """Handles downloading and processing AP support logs."""
    
    def __init__(self, client: RuckusOneClient, output_dir: str = ".", 
                 timeout: int = 300, max_retries: int = 10, retry_delay: int = 30):
        """
        Initialize AP log downloader.
        
        Args:
            client: RuckusOneClient instance
            output_dir: Directory to save log files
            timeout: Total timeout for log generation
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retry attempts
        """
        self.client = client
        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def request_log_generation(self, venue_id: str, ap_serial: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Request support log generation from API.
        
        Args:
            venue_id: Venue ID containing the AP
            ap_serial: AP serial number
            
        Returns:
            Tuple of (success, download_url, error_message)
        """
        endpoint = f"/venues/{venue_id}/aps/{ap_serial}/logs"
        
        try:
            logger.debug(f"Making request to: {endpoint}")
            response = self.client.request("GET", endpoint, raw_response=True)
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Log is ready, get download URL
                try:
                    data = response.json()
                    logger.debug(f"Response JSON: {data}")
                    download_url = data.get('fileUrl')
                    if download_url:
                        logger.debug(f"Found fileUrl: {download_url[:100]}...")
                        return True, download_url, None
                    else:
                        logger.debug(f"No fileUrl in response. Available fields: {list(data.keys())}")
                        return False, None, f"No fileUrl in response. Available fields: {list(data.keys())}"
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error: {e}")
                    logger.debug(f"Response text: {response.text[:500]}")
                    return False, None, "Invalid JSON response"
            
            elif response.status_code == 202:
                # Log generation in progress
                logger.debug("Log generation in progress (202 status)")
                return False, None, "Log generation in progress"
            
            elif response.status_code == 404:
                logger.debug("AP not found or logs endpoint not available (404 status)")
                return False, None, "AP not found or logs endpoint not available"
            
            else:
                logger.debug(f"Unexpected status code: {response.status_code}")
                logger.debug(f"Response text: {response.text[:500]}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f'HTTP {response.status_code}')
                    logger.debug(f"Error data: {error_data}")
                except:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                return False, None, error_msg
                
        except Exception as e:
            return False, None, f"API request failed: {str(e)}"
    
    def wait_for_log_generation(self, venue_id: str, ap_serial: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Wait for log generation to complete with retry logic.
        
        Args:
            venue_id: Venue ID containing the AP
            ap_serial: AP serial number
            
        Returns:
            Tuple of (success, download_url, error_message)
        """
        start_time = time.time()
        
        for attempt in range(1, self.max_retries + 1):
            if shutdown_requested:
                return False, None, "Shutdown requested"
            
            # Check if total timeout exceeded
            if time.time() - start_time > self.timeout:
                return False, None, f"Timeout exceeded ({self.timeout}s)"
            
            logger.debug(f"Attempt {attempt}/{self.max_retries} for AP {ap_serial}")
            success, download_url, error = self.request_log_generation(venue_id, ap_serial)
            
            if success and download_url:
                logger.debug(f"Log ready for AP {ap_serial} after {attempt} attempts")
                return True, download_url, None
            
            # If it's a permanent error (not "in progress"), stop retrying
            if error and "in progress" not in error.lower():
                return False, None, error
            
            # Wait before next attempt (unless it's the last attempt)
            if attempt < self.max_retries:
                logger.debug(f"Waiting {self.retry_delay}s before retry...")
                time.sleep(self.retry_delay)
        
        return False, None, f"Max retries ({self.max_retries}) exceeded"
    
    def download_log_file(self, download_url: str, ap_serial: str, keep_compressed: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download log file from URL and decompress.
        
        Args:
            download_url: Pre-signed URL to download log file
            ap_serial: AP serial number for filename
            keep_compressed: Whether to keep the compressed .gz file
            
        Returns:
            Tuple of (success, log_file_path, error_message)
        """
        try:
            # Create filenames with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"{ap_serial}_support_{timestamp}.log"
            gz_filename = f"{log_filename}.gz"
            log_path = self.output_dir / log_filename
            gz_path = self.output_dir / gz_filename
            
            # Download compressed file
            logger.debug(f"Downloading log for AP {ap_serial} from URL: {download_url[:100]}...")
            response = requests.get(download_url, stream=True, timeout=60)
            logger.debug(f"Download response status: {response.status_code}")
            logger.debug(f"Download response headers: {dict(response.headers)}")
            response.raise_for_status()
            
            # Save compressed file
            logger.debug(f"Saving compressed file to: {gz_path}")
            with open(gz_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            gz_size = os.path.getsize(gz_path)
            logger.debug(f"Downloaded compressed file size: {gz_size} bytes")
            
            # Decompress file
            logger.debug(f"Decompressing log for AP {ap_serial} to: {log_path}")
            with gzip.open(gz_path, 'rb') as f_in:
                with open(log_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            log_size = os.path.getsize(log_path)
            logger.debug(f"Decompressed file size: {log_size} bytes")
            
            # Remove compressed file if not keeping it
            if not keep_compressed:
                logger.debug(f"Removing compressed file: {gz_path}")
                os.remove(gz_path)
            else:
                logger.debug(f"Keeping compressed file: {gz_path}")
            
            logger.debug(f"Successfully downloaded and decompressed log for AP {ap_serial}")
            return True, str(log_path), None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Download failed: {str(e)}"
        except gzip.BadGzipFile:
            return False, None, "Downloaded file is not a valid gzip file"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def process_single_ap(self, ap_info: Dict[str, Any], keep_compressed: bool = False) -> Dict[str, Any]:
        """
        Process a single AP: request log generation, wait, and download.
        
        Args:
            ap_info: AP information dictionary
            keep_compressed: Whether to keep compressed files
            
        Returns:
            Dictionary with processing results
        """
        ap_serial = ap_info.get('serial_number', '')
        venue_id = ap_info.get('venue_id', '')
        
        result = {
            'ap_info': ap_info,
            'success': False,
            'download_url': None,
            'log_file_path': None,
            'error': None,
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Request log generation and wait for completion
            logger.debug(f"Requesting log generation for AP {ap_serial}")
            success, download_url, error = self.wait_for_log_generation(venue_id, ap_serial)
            
            if not success:
                result['error'] = error
                return result
            
            result['download_url'] = download_url
            
            # Step 2: Download and decompress the log file
            logger.debug(f"Downloading log file for AP {ap_serial}")
            success, log_path, error = self.download_log_file(download_url, ap_serial, keep_compressed)
            
            if not success:
                result['error'] = error
                return result
            
            result['log_file_path'] = log_path
            result['success'] = True
            
        except Exception as e:
            result['error'] = f"Unexpected error processing AP {ap_serial}: {str(e)}"
        finally:
            result['processing_time'] = time.time() - start_time
        
        return result

class LogAnalyzer:
    """Handles analysis of AP support log files."""
    
    def __init__(self, search_pattern: str = None):
        """
        Initialize log analyzer.
        
        Args:
            search_pattern: Regex pattern to search for in logs
        """
        # Default VXLAN configuration pattern
        self.default_pattern = r'n\s+u\s+vxlan0\s+1\s+(\w+)'
        self.search_pattern = search_pattern or self.default_pattern
        self.compiled_pattern = re.compile(self.search_pattern, re.MULTILINE | re.IGNORECASE)
    
    def analyze_log_file(self, log_file_path: str, ap_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single log file for patterns.
        
        Args:
            log_file_path: Path to the log file
            ap_info: AP information dictionary
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            'ap_info': ap_info,
            'log_file_path': log_file_path,
            'matches': [],
            'is_good_config': None,
            'analysis_summary': '',
            'error': None
        }
        
        try:
            if not os.path.exists(log_file_path):
                result['error'] = f"Log file not found: {log_file_path}"
                return result
            
            # Read log file
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            # Find all matches
            matches = self.compiled_pattern.findall(log_content)
            full_matches = self.compiled_pattern.finditer(log_content)
            
            # Store full matched lines
            for match in full_matches:
                result['matches'].append({
                    'line': match.group(0),
                    'groups': match.groups(),
                    'line_number': log_content[:match.start()].count('\n') + 1
                })
            
            # Analyze for VXLAN configuration if using default pattern
            if self.search_pattern == self.default_pattern:
                result['is_good_config'] = self._analyze_vxlan_config(matches)
                if result['is_good_config'] is True:
                    result['analysis_summary'] = "GOOD: VXLAN configuration ends with 'all'"
                elif result['is_good_config'] is False:
                    result['analysis_summary'] = f"BAD: VXLAN configuration ends with number: {matches}"
                else:
                    result['analysis_summary'] = "UNKNOWN: No VXLAN configuration found"
            else:
                # Custom pattern analysis
                if matches:
                    result['analysis_summary'] = f"Found {len(matches)} matches with custom pattern"
                else:
                    result['analysis_summary'] = "No matches found with custom pattern"
        
        except Exception as e:
            result['error'] = f"Error analyzing log file: {str(e)}"
        
        return result
    
    def _analyze_vxlan_config(self, matches: List[str]) -> Optional[bool]:
        """
        Analyze VXLAN configuration matches.
        
        Args:
            matches: List of matched groups from regex
            
        Returns:
            True if good config (ends with 'all'), False if bad, None if no matches
        """
        if not matches:
            return None
        
        # Check if any match ends with 'all' (good configuration)
        for match in matches:
            if match.lower() == 'all':
                return True
        
        # If we have matches but none end with 'all', it's bad configuration
        return False
    
    def analyze_existing_logs(self, log_dir: str, ap_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze existing log files in a directory.
        
        Args:
            log_dir: Directory containing log files
            ap_list: List of AP information
            
        Returns:
            List of analysis results
        """
        results = []
        log_dir_path = Path(log_dir)
        
        if not log_dir_path.exists():
            logger.error(f"Log directory not found: {log_dir}")
            return results
        
        # Create a mapping of serial numbers to AP info
        ap_map = {ap.get('serial_number', ''): ap for ap in ap_list}
        
        # Find all log files
        log_files = list(log_dir_path.glob("*_support.log"))
        logger.info(f"Found {len(log_files)} log files in {log_dir}")
        
        for log_file in log_files:
            # Extract serial number from filename (support both old and new formats)
            serial_match = re.match(r'([^_]+)_support(?:_\d{8}_\d{6})?\.log', log_file.name)
            if not serial_match:
                continue
            
            serial_number = serial_match.group(1)
            ap_info = ap_map.get(serial_number, {'serial_number': serial_number})
            
            # Analyze the log file
            analysis_result = self.analyze_log_file(str(log_file), ap_info)
            results.append(analysis_result)
        
        return results

class ParallelLogProcessor:
    """Manages parallel processing of AP logs with progress display."""
    
    def __init__(self, max_workers: int = 5, show_progress: bool = False):
        """
        Initialize parallel processor.
        
        Args:
            max_workers: Number of worker threads
            show_progress: Whether to show running progress
        """
        self.max_workers = max_workers
        self.show_progress = show_progress
        self.stats = {
            'total_aps': 0,
            'completed': 0,
            'good_configs': 0,
            'bad_configs': 0,
            'unknown_configs': 0,
            'failed_downloads': 0,
            'failed_analysis': 0
        }
        self.stats_lock = threading.Lock()
    
    def update_stats(self, download_result: Dict[str, Any], analysis_result: Dict[str, Any] = None):
        """Update processing statistics."""
        with self.stats_lock:
            self.stats['completed'] += 1
            
            if not download_result.get('success', False):
                self.stats['failed_downloads'] += 1
            elif analysis_result:
                if analysis_result.get('error'):
                    self.stats['failed_analysis'] += 1
                else:
                    is_good = analysis_result.get('is_good_config')
                    if is_good is True:
                        self.stats['good_configs'] += 1
                    elif is_good is False:
                        self.stats['bad_configs'] += 1
                    else:
                        self.stats['unknown_configs'] += 1
            
            # Display overall progress if enabled
            if self.show_progress:
                total_failed = self.stats['failed_downloads'] + self.stats['failed_analysis']
                display_overall_progress(
                    completed=self.stats['completed'],
                    total=self.stats['total_aps'],
                    good=self.stats['good_configs'],
                    bad=self.stats['bad_configs'],
                    unknown=self.stats['unknown_configs'],
                    failed=total_failed,
                    show_progress=True
                )
                print()  # Add newline after overall progress for readability
    
    def get_stats_summary(self) -> str:
        """Get current statistics as formatted string."""
        with self.stats_lock:
            remaining = self.stats['total_aps'] - self.stats['completed']
            return (f"[Complete: {colored(str(self.stats['completed']), 'GREEN')}] "
                   f"[Good: {colored(str(self.stats['good_configs']), 'GREEN')}] "
                   f"[Bad: {colored(str(self.stats['bad_configs']), 'RED')}] "
                   f"[Unknown: {colored(str(self.stats['unknown_configs']), 'YELLOW')}] "
                   f"[Failed: {colored(str(self.stats['failed_downloads'] + self.stats['failed_analysis']), 'RED')}] "
                   f"[Remaining: {remaining}]")
    
    def process_ap_logs(
        self, 
        ap_list: List[Dict[str, Any]], 
        downloader: APLogDownloader,
        analyzer: LogAnalyzer,
        keep_compressed: bool = False,
        search_enabled: bool = True,
        simulate: bool = False,
        resume: bool = False,
        batch_size: int = 50,
        checkpoint_file: str = None
    ) -> Dict[str, Any]:
        """
        Process AP logs with parallel downloading and analysis.
        
        Args:
            ap_list: List of APs to process
            downloader: APLogDownloader instance
            analyzer: LogAnalyzer instance
            keep_compressed: Whether to keep compressed files
            search_enabled: Whether to analyze logs after download
            simulate: Whether to simulate without actual downloads
            resume: Whether to resume from checkpoint
            batch_size: Save checkpoint every N APs
            checkpoint_file: Path to checkpoint file
            
        Returns:
            Dictionary with processing results
        """
        # Load checkpoint data if resuming
        checkpoint_data = {}
        processed_serials = set()
        start_index = 0
        if resume and checkpoint_file:
            checkpoint_data = load_checkpoint(checkpoint_file)
            start_index = checkpoint_data.get('last_processed_ap_index', 0)
            processed_serials = set(checkpoint_data.get('processed_serials', []))
            if processed_serials:
                logger.info(f"Resuming parallel processing, skipping {len(processed_serials)} already processed APs")
                # Restore stats
                for key, value in checkpoint_data.get('stats', {}).items():
                    if key in self.stats:
                        self.stats[key] = value
        
        # Filter out already processed APs
        remaining_ap_list = []
        for ap in ap_list:
            ap_serial = ap.get('serial_number', 'Unknown')
            if ap_serial not in processed_serials:
                remaining_ap_list.append(ap)
        
        if resume:
            logger.info(f"Processing {len(remaining_ap_list)} remaining APs in parallel (skipped {len(processed_serials)} already processed)")
        
        self.stats['total_aps'] = len(ap_list)  # Keep original total for progress tracking
        results = checkpoint_data.get('results', [])
        download_results = checkpoint_data.get('download_results', [])
        analysis_results = checkpoint_data.get('analysis_results', [])
        
        # Process downloads in parallel  
        logger.info(f"Processing {len(remaining_ap_list)} remaining APs with {self.max_workers} workers...")
        logger.info("Progress will be shown as individual APs complete...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit download tasks
            future_to_ap = {}
            
            for i, ap in enumerate(remaining_ap_list):
                if shutdown_requested:
                    break
                
                if simulate:
                    future = executor.submit(self._simulate_ap_processing, ap, i + 1, len(remaining_ap_list))
                else:
                    future = executor.submit(self._process_single_ap_wrapper, 
                                           downloader, analyzer, ap, i + 1, len(remaining_ap_list), 
                                           keep_compressed, search_enabled)
                future_to_ap[future] = ap
            
            # Collect results as they complete
            for future in as_completed(future_to_ap):
                if shutdown_requested:
                    break
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    download_result = result['download_result']
                    analysis_result = result.get('analysis_result')
                    
                    download_results.append(download_result)
                    if analysis_result:
                        analysis_results.append(analysis_result)
                    
                    self.update_stats(download_result, analysis_result)
                    
                    # Save checkpoint periodically
                    if checkpoint_file and self.stats['completed'] % batch_size == 0:
                        # Build processed serials list
                        completed_serials = list(processed_serials)
                        completed_serials.extend([r['ap_info'].get('serial_number', 'Unknown') 
                                                for r in results[len(checkpoint_data.get('results', [])):]])
                        
                        checkpoint_data_new = {
                            'last_processed_ap_index': self.stats['completed'],
                            'processed_serials': completed_serials,
                            'results': results,
                            'download_results': download_results,
                            'analysis_results': analysis_results,
                            'stats': dict(self.stats),
                            'timestamp': time.time()
                        }
                        save_checkpoint(checkpoint_file, checkpoint_data_new)
                        logger.debug(f"Parallel checkpoint saved after {self.stats['completed']} completed APs")
                    
                except Exception as e:
                    ap = future_to_ap[future]
                    logger.error(f"Error processing AP {ap.get('serial_number', 'Unknown')}: {e}")
                    self.stats['failed_downloads'] += 1
                    
                    # Save checkpoint on shutdown
                    if shutdown_requested and checkpoint_file:
                        # Build processed serials list
                        completed_serials = list(processed_serials)
                        completed_serials.extend([r['ap_info'].get('serial_number', 'Unknown') 
                                                for r in results[len(checkpoint_data.get('results', [])):]])
                        
                        checkpoint_data_new = {
                            'last_processed_ap_index': self.stats['completed'],
                            'processed_serials': completed_serials,
                            'results': results,
                            'download_results': download_results, 
                            'analysis_results': analysis_results,
                            'stats': dict(self.stats),
                            'timestamp': time.time()
                        }
                        save_checkpoint(checkpoint_file, checkpoint_data_new)
                        logger.info(f"Parallel checkpoint saved. Resume with --resume flag")
                        break
        
        # Final statistics
        final_stats = dict(self.stats)
        
        return {
            'results': results,
            'download_results': download_results,
            'analysis_results': analysis_results,
            'stats': final_stats
        }
    
    def _process_single_ap_wrapper(self, downloader: APLogDownloader, analyzer: LogAnalyzer,
                                  ap_info: Dict[str, Any], index: int, total: int,
                                  keep_compressed: bool, search_enabled: bool) -> Dict[str, Any]:
        """Wrapper for processing single AP with progress display."""
        ap_serial = ap_info.get('serial_number', 'Unknown')
        
        # In parallel mode, only show completion status to avoid overlapping progress lines
        logger.debug(f"[{index}/{total}] Starting {ap_serial}")
        
        # Step 1: Download log
        download_result = downloader.process_single_ap(ap_info, keep_compressed)
        
        result = {
            'ap_info': ap_info,
            'download_result': download_result,
            'analysis_result': None
        }
        
        if not download_result.get('success'):
            logger.info(f"[{index}/{total}] FAILED {ap_serial}: {download_result.get('error', 'Unknown error')}")
            return result
        
        # Step 2: Analyze log if enabled
        if search_enabled:
            log_path = download_result.get('log_file_path')
            if log_path:
                analysis_result = analyzer.analyze_log_file(log_path, ap_info)
                result['analysis_result'] = analysis_result
        
        # Show completion status
        if result.get('analysis_result'):
            config_status = result['analysis_result'].get('is_good_config')
            if config_status is True:
                logger.info(f"[{index}/{total}] COMPLETE {ap_serial}: GOOD configuration")
            elif config_status is False:
                logger.info(f"[{index}/{total}] COMPLETE {ap_serial}: BAD configuration")
            else:
                logger.info(f"[{index}/{total}] COMPLETE {ap_serial}: UNKNOWN configuration")
        else:
            logger.info(f"[{index}/{total}] COMPLETE {ap_serial}: Downloaded (no analysis)")
        
        return result
    
    def _simulate_ap_processing(self, ap_info: Dict[str, Any], index: int, total: int) -> Dict[str, Any]:
        """Simulate AP processing for dry run."""
        import random
        
        print_progress(index, total, ap_info, "Starting", 0)
        time.sleep(0.2)
        
        print_progress(index, total, ap_info, "Requesting", 25)
        time.sleep(0.3)
        
        print_progress(index, total, ap_info, "Downloading", 60)
        time.sleep(0.4)
        
        print_progress(index, total, ap_info, "Analyzing", 85)
        time.sleep(0.2)
        
        # Simulate random results
        success = random.random() > 0.1  # 90% success rate
        is_good = random.choice([True, False, None]) if success else None
        
        download_result = {
            'ap_info': ap_info,
            'success': success,
            'log_file_path': f"{ap_info.get('serial_number', 'unknown')}_support.log" if success else None,
            'error': None if success else "Simulated failure",
            'processing_time': random.uniform(5, 30)
        }
        
        analysis_result = None
        if success:
            analysis_result = {
                'ap_info': ap_info,
                'is_good_config': is_good,
                'matches': ["simulated match"],
                'analysis_summary': f"Simulated: {'GOOD' if is_good else 'BAD' if is_good is False else 'UNKNOWN'}",
                'error': None
            }
        
        print_progress(index, total, ap_info, "Complete", 100, final=True)
        
        return {
            'ap_info': ap_info,
            'download_result': download_result,
            'analysis_result': analysis_result
        }

def process_ap_logs_sequential(
    ap_list: List[Dict[str, Any]],
    downloader: APLogDownloader,
    analyzer: LogAnalyzer,
    keep_compressed: bool = False,
    search_enabled: bool = True,
    simulate: bool = False,
    delay: int = 0,
    show_progress: bool = False,
    resume: bool = False,
    batch_size: int = 50,
    checkpoint_file: str = None
) -> Dict[str, Any]:
    """
    Process AP logs sequentially with progress display.
    
    Args:
        ap_list: List of APs to process
        downloader: APLogDownloader instance
        analyzer: LogAnalyzer instance
        keep_compressed: Whether to keep compressed files
        search_enabled: Whether to analyze logs after download
        simulate: Whether to simulate without actual downloads
        delay: Delay between AP processing in seconds
        resume: Whether to resume from checkpoint
        batch_size: Save checkpoint every N APs
        checkpoint_file: Path to checkpoint file
        
    Returns:
        Dictionary with processing results
    """
    results = []
    download_results = []
    analysis_results = []
    
    # Load checkpoint data if resuming
    checkpoint_data = {}
    start_ap_index = 0
    if resume and checkpoint_file:
        checkpoint_data = load_checkpoint(checkpoint_file)
        start_ap_index = checkpoint_data.get('last_processed_ap_index', 0)
        if start_ap_index > 0:
            logger.info(f"Resuming from AP {start_ap_index + 1}/{len(ap_list)}")
            # Restore previous results
            results = checkpoint_data.get('results', [])
            download_results = checkpoint_data.get('download_results', [])
            analysis_results = checkpoint_data.get('analysis_results', [])
    
    stats = {
        'total_aps': len(ap_list),
        'completed': start_ap_index,
        'good_configs': checkpoint_data.get('stats', {}).get('good_configs', 0),
        'bad_configs': checkpoint_data.get('stats', {}).get('bad_configs', 0),
        'unknown_configs': checkpoint_data.get('stats', {}).get('unknown_configs', 0),
        'failed_downloads': checkpoint_data.get('stats', {}).get('failed_downloads', 0),
        'failed_analysis': checkpoint_data.get('stats', {}).get('failed_analysis', 0)
    }
    
    remaining_aps = len(ap_list) - start_ap_index
    logger.info(f"Processing {remaining_aps} APs sequentially (starting from index {start_ap_index})...")
    
    for i, ap in enumerate(ap_list):
        if shutdown_requested:
            logger.warning("Shutdown requested, stopping processing")
            break
        
        # Skip already processed APs when resuming
        if i < start_ap_index:
            continue
        
        ap_serial = ap.get('serial_number', 'Unknown')
        
        # Show starting progress
        print_progress(i + 1, len(ap_list), ap, "Starting", 0)
        
        result = {
            'ap_info': ap,
            'download_result': None,
            'analysis_result': None
        }
        
        if simulate:
            # Simulate processing
            print_progress(i + 1, len(ap_list), ap, "Requesting", 25)
            time.sleep(0.5)
            print_progress(i + 1, len(ap_list), ap, "Downloading", 60)
            time.sleep(0.5)
            print_progress(i + 1, len(ap_list), ap, "Analyzing", 85)
            time.sleep(0.3)
            
            # Create simulated results
            download_result = {
                'ap_info': ap,
                'success': True,
                'log_file_path': f"{ap_serial}_support.log",
                'error': None,
                'processing_time': 1.3
            }
            
            analysis_result = {
                'ap_info': ap,
                'is_good_config': True,
                'matches': ["simulated match"],
                'analysis_summary': "SIMULATED: GOOD configuration",
                'error': None
            }
            
            result['download_result'] = download_result
            result['analysis_result'] = analysis_result
            stats['good_configs'] += 1
            
        else:
            # Actual processing
            print_progress(i + 1, len(ap_list), ap, "Requesting", 20)
            download_result = downloader.process_single_ap(ap, keep_compressed)
            result['download_result'] = download_result
            download_results.append(download_result)
            
            if download_result.get('success'):
                print_progress(i + 1, len(ap_list), ap, "Downloading", 70)
                
                if search_enabled:
                    print_progress(i + 1, len(ap_list), ap, "Analyzing", 90)
                    log_path = download_result.get('log_file_path')
                    if log_path:
                        analysis_result = analyzer.analyze_log_file(log_path, ap)
                        result['analysis_result'] = analysis_result
                        analysis_results.append(analysis_result)
                        
                        # Update stats
                        is_good = analysis_result.get('is_good_config')
                        if analysis_result.get('error'):
                            stats['failed_analysis'] += 1
                        elif is_good is True:
                            stats['good_configs'] += 1
                        elif is_good is False:
                            stats['bad_configs'] += 1
                        else:
                            stats['unknown_configs'] += 1
            else:
                stats['failed_downloads'] += 1
        
        results.append(result)
        stats['completed'] += 1
        
        # Show individual AP completion
        print_progress(i + 1, len(ap_list), ap, "Complete", 100, final=True)
        
        # Display overall progress if enabled (always show this after individual AP)
        if show_progress:
            total_failed = stats['failed_downloads'] + stats['failed_analysis']
            display_overall_progress(
                completed=stats['completed'],
                total=len(ap_list),
                good=stats['good_configs'],
                bad=stats['bad_configs'],
                unknown=stats['unknown_configs'],
                failed=total_failed,
                show_progress=True
            )
            print()  # Add newline after overall progress for readability
        
        # Save checkpoint periodically
        if checkpoint_file and (i + 1) % batch_size == 0:
            checkpoint_data = {
                'last_processed_ap_index': i + 1,
                'results': results,
                'download_results': download_results,
                'analysis_results': analysis_results,
                'stats': stats,
                'timestamp': time.time()
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.debug(f"Checkpoint saved after processing {i + 1} APs")
        
        # Save checkpoint on shutdown
        if shutdown_requested and checkpoint_file:
            checkpoint_data = {
                'last_processed_ap_index': i + 1,
                'results': results,
                'download_results': download_results, 
                'analysis_results': analysis_results,
                'stats': stats,
                'timestamp': time.time()
            }
            save_checkpoint(checkpoint_file, checkpoint_data)
            logger.info(f"Checkpoint saved. Resume with --resume flag")
            break
        
        # Apply delay between APs
        if delay > 0 and i < len(ap_list) - 1:
            logger.info(f"Waiting {delay}s before next AP...")
            time.sleep(delay)
    
    return {
        'results': results,
        'download_results': download_results,
        'analysis_results': analysis_results,
        'stats': stats
    }

class ReportGenerator:
    """Generates reports for AP log processing results."""
    
    def __init__(self):
        """Initialize report generator."""
        pass
    
    def generate_console_report(self, results: Dict[str, Any]) -> str:
        """
        Generate console summary report.
        
        Args:
            results: Processing results dictionary
            
        Returns:
            Formatted report string
        """
        stats = results.get('stats', {})
        analysis_results = results.get('analysis_results', [])
        
        lines = []
        lines.append("="*80)
        lines.append(colored("AP SUPPORT LOG PROCESSING SUMMARY", 'WHITE', bold=True))
        lines.append("="*80)
        
        # Overall statistics
        total = stats.get('total_aps', 0)
        completed = stats.get('completed', 0)
        good = stats.get('good_configs', 0)
        bad = stats.get('bad_configs', 0)
        unknown = stats.get('unknown_configs', 0)
        failed_downloads = stats.get('failed_downloads', 0)
        failed_analysis = stats.get('failed_analysis', 0)
        
        lines.append(f"Total APs processed: {total}")
        lines.append(f"Successfully completed: {colored(str(completed), 'GREEN')}")
        lines.append(f"Failed downloads: {colored(str(failed_downloads), 'RED' if failed_downloads > 0 else 'GREEN')}")
        lines.append(f"Failed analysis: {colored(str(failed_analysis), 'RED' if failed_analysis > 0 else 'GREEN')}")
        lines.append("")
        
        # Configuration analysis
        analyzed_total = good + bad + unknown
        if analyzed_total > 0:
            lines.append("CONFIGURATION ANALYSIS:")
            good_pct = (good / analyzed_total) * 100 if analyzed_total > 0 else 0
            bad_pct = (bad / analyzed_total) * 100 if analyzed_total > 0 else 0
            unknown_pct = (unknown / analyzed_total) * 100 if analyzed_total > 0 else 0
            
            lines.append(f"  Good configurations: {colored(str(good), 'GREEN')} ({good_pct:.1f}%)")
            lines.append(f"  Bad configurations: {colored(str(bad), 'RED')} ({bad_pct:.1f}%)")
            lines.append(f"  Unknown configurations: {colored(str(unknown), 'YELLOW')} ({unknown_pct:.1f}%)")
        
        lines.append("="*80)
        
        report = "\n".join(lines)
        print(report)
        return report
    
    def generate_detailed_report(self, results: Dict[str, Any], report_file: str = None) -> str:
        """
        Generate detailed text report.
        
        Args:
            results: Processing results dictionary
            report_file: Optional output file path
            
        Returns:
            Formatted detailed report
        """
        stats = results.get('stats', {})
        analysis_results = results.get('analysis_results', [])
        download_results = results.get('download_results', [])
        
        lines = []
        lines.append("="*80)
        lines.append("AP SUPPORT LOG PROCESSING DETAILED REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("="*80)
        
        # Statistics section
        lines.append("\nSTATISTICS:")
        for key, value in stats.items():
            lines.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Good configurations
        good_aps = [r for r in analysis_results if r.get('is_good_config') is True]
        if good_aps:
            lines.append(f"\nGOOD CONFIGURATIONS ({len(good_aps)} APs):")
            for result in good_aps:
                ap_info = result.get('ap_info', {})
                ap_name = ap_info.get('name', 'Unknown')
                ap_serial = ap_info.get('serial_number', 'Unknown')
                venue_name = ap_info.get('venue_name', 'Unknown')
                summary = result.get('analysis_summary', '')
                
                lines.append(f"  ✓ {venue_name} - {ap_name} (SN: {ap_serial})")
                if result.get('matches'):
                    for match in result['matches'][:1]:  # Show first match
                        lines.append(f"    Match: {match.get('line', '').strip()}")
        
        # Bad configurations
        bad_aps = [r for r in analysis_results if r.get('is_good_config') is False]
        if bad_aps:
            lines.append(f"\nBAD CONFIGURATIONS ({len(bad_aps)} APs):")
            for result in bad_aps:
                ap_info = result.get('ap_info', {})
                ap_name = ap_info.get('name', 'Unknown')
                ap_serial = ap_info.get('serial_number', 'Unknown')
                venue_name = ap_info.get('venue_name', 'Unknown')
                
                lines.append(f"  ✗ {venue_name} - {ap_name} (SN: {ap_serial})")
                if result.get('matches'):
                    for match in result['matches'][:1]:  # Show first match
                        lines.append(f"    Match: {match.get('line', '').strip()}")
        
        # Unknown configurations
        unknown_aps = [r for r in analysis_results if r.get('is_good_config') is None]
        if unknown_aps:
            lines.append(f"\nUNKNOWN CONFIGURATIONS ({len(unknown_aps)} APs):")
            for result in unknown_aps:
                ap_info = result.get('ap_info', {})
                ap_name = ap_info.get('name', 'Unknown')
                ap_serial = ap_info.get('serial_number', 'Unknown')
                venue_name = ap_info.get('venue_name', 'Unknown')
                
                lines.append(f"  ? {venue_name} - {ap_name} (SN: {ap_serial})")
                lines.append(f"    {result.get('analysis_summary', 'No pattern matches found')}")
        
        # Failures
        failed_downloads = [r for r in download_results if not r.get('success', False)]
        if failed_downloads:
            lines.append(f"\nFAILED DOWNLOADS ({len(failed_downloads)} APs):")
            for result in failed_downloads:
                ap_info = result.get('ap_info', {})
                ap_name = ap_info.get('name', 'Unknown')
                ap_serial = ap_info.get('serial_number', 'Unknown')
                venue_name = ap_info.get('venue_name', 'Unknown')
                error = result.get('error', 'Unknown error')
                
                lines.append(f"  ✗ {venue_name} - {ap_name} (SN: {ap_serial})")
                lines.append(f"    Error: {error}")
        
        lines.append("\n" + "="*80)
        
        report = "\n".join(lines)
        
        # Save to file if specified
        if report_file:
            try:
                with open(report_file, 'w') as f:
                    f.write(report)
                logger.info(f"Detailed report saved to: {report_file}")
            except Exception as e:
                logger.error(f"Failed to save report to {report_file}: {e}")
        
        return report
    
    def export_good_aps_csv(self, results: Dict[str, Any], output_file: str):
        """
        Export APs with good configurations to CSV.
        
        Args:
            results: Processing results dictionary
            output_file: Output CSV file path
        """
        # Try analysis_results first, then fall back to results structure
        analysis_results = results.get('analysis_results', [])
        if not analysis_results and results.get('results'):
            analysis_results = [r.get('analysis_result') for r in results['results'] if r.get('analysis_result')]
        
        good_aps = [r for r in analysis_results if r.get('is_good_config') is True]
        
        if not good_aps:
            logger.warning("No good APs to export")
            return
        
        try:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['serial_number', 'name', 'venue_name', 'analysis_summary', 'match_line']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in good_aps:
                    ap_info = result.get('ap_info', {})
                    match_line = ''
                    if result.get('matches'):
                        match_line = result['matches'][0].get('line', '').strip()
                    
                    writer.writerow({
                        'serial_number': ap_info.get('serial_number', ''),
                        'name': ap_info.get('name', ''),
                        'venue_name': ap_info.get('venue_name', ''),
                        'analysis_summary': result.get('analysis_summary', ''),
                        'match_line': match_line
                    })
            
            logger.info(f"Good APs CSV exported to: {output_file} ({len(good_aps)} APs)")
            
        except Exception as e:
            logger.error(f"Failed to export good APs CSV: {e}")
    
    def export_bad_aps_csv(self, results: Dict[str, Any], output_file: str):
        """
        Export APs with bad configurations to CSV.
        
        Args:
            results: Processing results dictionary
            output_file: Output CSV file path
        """
        # Try analysis_results first, then fall back to results structure
        analysis_results = results.get('analysis_results', [])
        if not analysis_results and results.get('results'):
            analysis_results = [r.get('analysis_result') for r in results['results'] if r.get('analysis_result')]
        
        bad_aps = [r for r in analysis_results if r.get('is_good_config') is False]
        
        if not bad_aps:
            logger.warning("No bad APs to export")
            return
        
        try:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['serial_number', 'name', 'venue_name', 'analysis_summary', 'match_line']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in bad_aps:
                    ap_info = result.get('ap_info', {})
                    match_line = ''
                    if result.get('matches'):
                        match_line = result['matches'][0].get('line', '').strip()
                    
                    writer.writerow({
                        'serial_number': ap_info.get('serial_number', ''),
                        'name': ap_info.get('name', ''),
                        'venue_name': ap_info.get('venue_name', ''),
                        'analysis_summary': result.get('analysis_summary', ''),
                        'match_line': match_line
                    })
            
            logger.info(f"Bad APs CSV exported to: {output_file} ({len(bad_aps)} APs)")
            
        except Exception as e:
            logger.error(f"Failed to export bad APs CSV: {e}")
    
    def export_all_results_csv(self, results: Dict[str, Any], output_file: str):
        """
        Export all results to CSV.
        
        Args:
            results: Processing results dictionary
            output_file: Output CSV file path
        """
        all_results = results.get('results', [])
        
        if not all_results:
            logger.warning("No results to export")
            return
        
        try:
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = [
                    'serial_number', 'name', 'venue_name', 'download_success', 'download_error',
                    'log_file_path', 'analysis_success', 'is_good_config', 'analysis_summary',
                    'match_line', 'processing_time'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in all_results:
                    ap_info = result.get('ap_info', {})
                    download_result = result.get('download_result', {})
                    analysis_result = result.get('analysis_result', {})
                    
                    match_line = ''
                    if analysis_result and analysis_result.get('matches'):
                        matches = analysis_result['matches']
                        if matches and isinstance(matches[0], dict):
                            match_line = matches[0].get('line', '').strip()
                        elif matches and isinstance(matches[0], str):
                            match_line = matches[0].strip()
                    
                    writer.writerow({
                        'serial_number': ap_info.get('serial_number', ''),
                        'name': ap_info.get('name', ''),
                        'venue_name': ap_info.get('venue_name', ''),
                        'download_success': download_result.get('success', False),
                        'download_error': download_result.get('error', ''),
                        'log_file_path': download_result.get('log_file_path', ''),
                        'analysis_success': not bool(analysis_result.get('error')) if analysis_result else False,
                        'is_good_config': analysis_result.get('is_good_config') if analysis_result else None,
                        'analysis_summary': analysis_result.get('analysis_summary', '') if analysis_result else '',
                        'match_line': match_line,
                        'processing_time': download_result.get('processing_time', 0)
                    })
            
            logger.info(f"All results CSV exported to: {output_file} ({len(all_results)} APs)")
            
        except Exception as e:
            logger.error(f"Failed to export all results CSV: {e}")

def main():
    """Main function."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='RUCKUS One AP Support Log Downloader and Analyzer',
        epilog='''
Examples:
  # Export all APs to CSV
  %(prog)s --config config.ini --export
  
  # Download and analyze logs with default VXLAN pattern
  %(prog)s --config config.ini --import-aps aps.csv
  
  # Use custom search pattern
  %(prog)s --config config.ini --import-aps aps.csv --search-pattern "error.*connection"
  
  # Search existing logs only (no downloads)
  %(prog)s --search-only --log-dir ./logs --import-aps aps.csv
  
  # Parallel processing with 10 workers
  %(prog)s --config config.ini --import-aps aps.csv --parallel 10
  
  # Generate detailed reports and CSV exports
  %(prog)s --config config.ini --import-aps aps.csv --report-file report.txt --good-aps-csv good.csv --bad-aps-csv bad.csv
  
  # Simulate processing (dry run)
  %(prog)s --config config.ini --import-aps aps.csv --simulate
  
  # Resume from checkpoint after interruption
  %(prog)s --resume

Default VXLAN search pattern: n\\s+u\\s+vxlan0\\s+1\\s+(\\w+)
Good config: line ends with 'all'
Bad config: line ends with number (e.g., '1')
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    config_group = parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--config', 
                             help='Path to config.ini file with RUCKUS One credentials')
    config_group.add_argument('--search-only', action='store_true',
                             help='Search existing logs only (no API access required)')
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--export', action='store_true',
                             help='Export all APs to CSV file')
    action_group.add_argument('--import-aps',
                             help='Import AP list from CSV file for processing')
    
    # Processing options
    parser.add_argument('--output-dir', default='.',
                       help='Directory to save log files (default: current directory)')
    parser.add_argument('--search-pattern',
                       help='Regex pattern to search in logs (default: VXLAN pattern)')
    parser.add_argument('--parallel', type=int, default=5,
                       help='Number of parallel workers (1-20, default: 5)')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for log generation in seconds (default: 300)')
    parser.add_argument('--max-retries', type=int, default=10,
                       help='Maximum retry attempts for log generation (default: 10)')
    parser.add_argument('--retry-delay', type=int, default=30,
                       help='Delay between retries in seconds (default: 30)')
    
    # Output options
    parser.add_argument('--output',
                       help='Custom output filename for --export')
    parser.add_argument('--report-file',
                       help='Save detailed report to text file')
    parser.add_argument('--good-aps-csv',
                       help='Export good configuration APs to CSV')
    parser.add_argument('--bad-aps-csv',
                       help='Export bad configuration APs to CSV')
    parser.add_argument('--all-results-csv',
                       help='Export all results to CSV')
    
    # Behavior options
    parser.add_argument('--keep-compressed', action='store_true',
                       help='Keep compressed .gz files after decompression')
    parser.add_argument('--no-search', action='store_true',
                       help='Download logs but skip pattern analysis')
    parser.add_argument('--simulate', action='store_true',
                       help='Simulate processing without actual downloads')
    parser.add_argument('--force', action='store_true',
                       help='Process more than 100 APs without confirmation')
    parser.add_argument('--delay', type=int, default=0,
                       help='Delay between AP processing in sequential mode (seconds)')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from last checkpoint')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Save checkpoint every N APs (default: 50)')
    
    # Search-only mode options
    parser.add_argument('--log-dir', default='.',
                       help='Directory containing existing log files (for --search-only)')
    
    # Logging options
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Set logging verbosity level')
    parser.add_argument('--log-file',
                       help='Write logs to specified file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with detailed logging to console')
    parser.add_argument('--show-progress', action='store_true',
                       help='Show running totals and progress bar during processing')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.parallel < 1 or args.parallel > 20:
        parser.error("--parallel must be between 1 and 20")
    
    if args.search_only and not args.import_aps:
        parser.error("--search-only requires --import-aps to specify AP list")
    
    if args.export and args.search_only:
        parser.error("Cannot use --export with --search-only")
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else args.log_level
    setup_logging(log_level, args.log_file)
    
    # Initialize session directory variables
    full_output_dir = args.output_dir
    session_dir = None
    
    try:
        if args.search_only:
            # Search-only mode - analyze existing log files
            logger.info("Running in search-only mode")
            
            # Load AP list for context
            ap_list = load_aps_csv(args.import_aps)
            
            # Initialize analyzer
            analyzer = LogAnalyzer(args.search_pattern)
            
            # Analyze existing logs
            analysis_results = analyzer.analyze_existing_logs(args.log_dir, ap_list)
            
            if not analysis_results:
                logger.error("No log files found or analyzed")
                sys.exit(1)
            
            # Generate statistics
            stats = {
                'total_aps': len(analysis_results),
                'completed': len(analysis_results),
                'good_configs': len([r for r in analysis_results if r.get('is_good_config') is True]),
                'bad_configs': len([r for r in analysis_results if r.get('is_good_config') is False]),
                'unknown_configs': len([r for r in analysis_results if r.get('is_good_config') is None]),
                'failed_downloads': 0,
                'failed_analysis': len([r for r in analysis_results if r.get('error')])
            }
            
            results = {
                'stats': stats,
                'analysis_results': analysis_results,
                'download_results': [],
                'results': [{'ap_info': r.get('ap_info', {}), 'analysis_result': r} for r in analysis_results]
            }
            
        else:
            # Regular processing mode
            config = load_config(args.config)
            
            logger.info(f"Initializing RUCKUS One client (region: {config.get('region', 'na')})")
            client = RuckusOneClient(
                client_id=config['client_id'],
                client_secret=config['client_secret'],
                tenant_id=config['tenant_id'],
                region=config.get('region', 'na')
            )
            
            if args.export:
                # Export mode
                logger.info("Exporting all APs to CSV...")
                output_file = export_aps_to_csv(client, args.output)
                if output_file:
                    print(f"\nAP export completed: {output_file}")
                    print("Edit the CSV file to select APs for processing, then use --import-aps")
                sys.exit(0)
                
            else:
                # Processing mode
                ap_list = load_aps_csv(args.import_aps)
                
                # Filter for operational APs only (support logs only available for operational APs)
                def is_operational(ap):
                    status = ap.get('status', '')
                    return 'Operational' in status or status.startswith('2_')
                
                operational_aps = [ap for ap in ap_list if is_operational(ap)]
                non_operational_aps = [ap for ap in ap_list if not is_operational(ap)]
                
                logger.info(f"Loaded {len(ap_list)} total APs: {len(operational_aps)} operational, {len(non_operational_aps)} non-operational")
                logger.info(f"Processing {len(operational_aps)} operational APs (support logs only available for operational APs)")
                
                if len(non_operational_aps) > 0:
                    logger.info(f"Skipping {len(non_operational_aps)} non-operational APs: {[ap.get('name', 'Unknown') for ap in non_operational_aps[:5]]}" + 
                               (f" and {len(non_operational_aps) - 5} more" if len(non_operational_aps) > 5 else ""))
                
                # Use operational APs for processing
                ap_list = operational_aps
                
                if len(ap_list) == 0:
                    logger.error("No operational APs found to process")
                    sys.exit(1)
                
                if len(ap_list) > 100 and not args.force and not args.simulate:
                    response = input(f"About to process {len(ap_list)} operational APs. This may take a long time. Continue? (yes/no): ")
                    if response.lower() != 'yes':
                        logger.info("Processing cancelled by user")
                        sys.exit(0)
                
                # Create timestamped directory for this session
                session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                session_dir = f"ap_support_logs_{session_timestamp}"
                full_output_dir = os.path.join(args.output_dir, session_dir)
                
                # Create the directory
                os.makedirs(full_output_dir, exist_ok=True)
                logger.info(f"Created session directory: {full_output_dir}")
                
                # Checkpoint handling
                checkpoint_file = None
                if args.resume:
                    # Look for existing checkpoint files
                    checkpoint_files = [f for f in os.listdir('.') if f.startswith('.checkpoint_ap_support_')]
                    if checkpoint_files:
                        checkpoint_file = sorted(checkpoint_files)[-1]  # Use the most recent
                        logger.info(f"Found checkpoint file: {checkpoint_file}")
                    else:
                        logger.warning("No checkpoint file found to resume from")
                        args.resume = False
                
                if not args.resume:
                    # Create new checkpoint file
                    checkpoint_file = f".checkpoint_ap_support_{int(time.time())}.json"
                
                # Initialize components
                downloader = APLogDownloader(
                    client=client,
                    output_dir=full_output_dir,
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    retry_delay=args.retry_delay
                )
                
                analyzer = LogAnalyzer(args.search_pattern)
                search_enabled = not args.no_search
                
                # Process APs
                if args.parallel > 1:
                    # Parallel processing
                    logger.info(f"Using parallel processing with {args.parallel} workers")
                    processor = ParallelLogProcessor(max_workers=args.parallel, show_progress=args.show_progress)
                    results = processor.process_ap_logs(
                        ap_list=ap_list,
                        downloader=downloader,
                        analyzer=analyzer,
                        keep_compressed=args.keep_compressed,
                        search_enabled=search_enabled,
                        simulate=args.simulate,
                        resume=args.resume,
                        batch_size=args.batch_size,
                        checkpoint_file=checkpoint_file
                    )
                else:
                    # Sequential processing
                    logger.info("Using sequential processing (1 AP at a time)")
                    results = process_ap_logs_sequential(
                        ap_list=ap_list,
                        downloader=downloader,
                        analyzer=analyzer,
                        keep_compressed=args.keep_compressed,
                        search_enabled=search_enabled,
                        simulate=args.simulate,
                        delay=args.delay,
                        show_progress=args.show_progress,
                        resume=args.resume,
                        batch_size=args.batch_size,
                        checkpoint_file=checkpoint_file
                    )
        
        # Add newline after progress display if it was shown
        if args.show_progress and not args.search_only:
            print()  # Move to next line after progress display
        
        # Generate reports
        report_generator = ReportGenerator()
        
        # Console summary
        report_generator.generate_console_report(results)
        
        # Adjust report file paths to use session directory
        if not args.search_only:
            # For non-search-only mode, put reports in session directory
            report_base_dir = full_output_dir
        else:
            # For search-only mode, use current directory or specified output dir
            report_base_dir = args.output_dir if args.output_dir != '.' else '.'
        
        # Detailed report
        if args.report_file:
            if not os.path.isabs(args.report_file):
                report_file_path = os.path.join(report_base_dir, args.report_file)
            else:
                report_file_path = args.report_file
            report_generator.generate_detailed_report(results, report_file_path)
        
        # CSV exports
        if args.good_aps_csv:
            if not os.path.isabs(args.good_aps_csv):
                good_csv_path = os.path.join(report_base_dir, args.good_aps_csv)
            else:
                good_csv_path = args.good_aps_csv
            report_generator.export_good_aps_csv(results, good_csv_path)
        
        if args.bad_aps_csv:
            if not os.path.isabs(args.bad_aps_csv):
                bad_csv_path = os.path.join(report_base_dir, args.bad_aps_csv)
            else:
                bad_csv_path = args.bad_aps_csv
            report_generator.export_bad_aps_csv(results, bad_csv_path)
        
        if args.all_results_csv:
            if not os.path.isabs(args.all_results_csv):
                all_csv_path = os.path.join(report_base_dir, args.all_results_csv)
            else:
                all_csv_path = args.all_results_csv
            report_generator.export_all_results_csv(results, all_csv_path)
        
        # Final summary
        stats = results.get('stats', {})
        mode = "SIMULATION" if args.simulate else "SEARCH-ONLY" if args.search_only else "PROCESSING"
        logger.info(f"\n{mode} completed successfully")
        logger.info(f"Summary: {stats.get('completed', 0)} processed, "
                   f"{stats.get('good_configs', 0)} good, "
                   f"{stats.get('bad_configs', 0)} bad, "
                   f"{stats.get('failed_downloads', 0) + stats.get('failed_analysis', 0)} failed")
        
        # Clean up checkpoint file on successful completion
        if not args.search_only and checkpoint_file and os.path.exists(checkpoint_file):
            try:
                os.remove(checkpoint_file)
                logger.debug(f"Checkpoint file {checkpoint_file} removed after successful completion")
            except Exception as e:
                logger.warning(f"Could not remove checkpoint file {checkpoint_file}: {e}")
        
        # Show session directory location for downloads
        if not args.search_only and session_dir:
            logger.info(f"All files saved to: {full_output_dir}")
            print(f"\nSession directory: {colored(full_output_dir, 'GREEN', bold=True)}")
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()