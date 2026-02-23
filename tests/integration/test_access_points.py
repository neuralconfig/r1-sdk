#!/usr/bin/env python3
"""
Test script for the Access Points module of the RUCKUS One API.

This script tests various operations related to access points, including
listing access points, getting access point details, and other AP operations.

Usage:
    python test_access_points.py
"""

import os
import sys
import logging
import configparser
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.access_points import AccessPoints
from ruckus_one.exceptions import ResourceNotFoundError

def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini')
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

def init_client():
    """Initialize the RUCKUS One client with credentials."""
    # First try to load from config file
    config = load_config()
    
    # Then try environment variables or fall back to input
    client_id = os.environ.get("RUCKUS_CLIENT_ID") or config.get('client_id')
    client_secret = os.environ.get("RUCKUS_CLIENT_SECRET") or config.get('client_secret')
    tenant_id = os.environ.get("RUCKUS_TENANT_ID") or config.get('tenant_id')
    region = os.environ.get("RUCKUS_REGION") or config.get('region', 'na')
    
    if not all([client_id, client_secret, tenant_id]) or \
       any(x in [client_id, client_secret, tenant_id] for x in ['YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', 'YOUR_TENANT_ID']):
        print("Please provide your RUCKUS One credentials:")
        if not client_id or client_id == 'YOUR_CLIENT_ID':
            client_id = input("Client ID: ")
        if not client_secret or client_secret == 'YOUR_CLIENT_SECRET':
            client_secret = input("Client Secret: ")
        if not tenant_id or tenant_id == 'YOUR_TENANT_ID':
            tenant_id = input("Tenant ID: ")
    
    # Initialize the client
    logger.info(f"Initializing client with region: {region}")
    client = RuckusOneClient(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id, region=region)
    return client

def test_list_aps(ap_module: AccessPoints):
    """Test listing access points."""
    logger.info("Testing list_aps...")
    try:
        # Test with default parameters
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = ap_module.list(query_data)
        aps = result.get('data', [])
        logger.info(f"Found {len(aps)} access points")
        
        # Print first AP details
        if aps:
            first_ap = aps[0]
            logger.info(f"First AP: {first_ap.get('name')} (Serial: {first_ap.get('serialNumber')})")
        
        # Test with pagination
        query_data_page = {
            "pageSize": 2,
            "page": 0,
            "sortOrder": "ASC"
        }
        result_page = ap_module.list(query_data_page)
        aps_page = result_page.get('data', [])
        logger.info(f"Found {len(aps_page)} access points in first page")
        
        # Test with venue filter (if available)
        if aps:
            venue_id = aps[0].get('venueId')
            if venue_id:
                query_data_venue = {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC",
                    "filters": [
                        {
                            "type": "VENUE",
                            "value": venue_id
                        }
                    ]
                }
                result_venue = ap_module.list(query_data_venue)
                aps_venue = result_venue.get('data', [])
                logger.info(f"Found {len(aps_venue)} access points in venue {venue_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_aps: {e}")
        return False

def test_get_ap(ap_module: AccessPoints):
    """Test getting an access point by ID."""
    logger.info("Testing get_ap...")
    try:
        # First, get a list of APs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = ap_module.list(query_data)
        aps = result.get('data', [])
        
        if not aps:
            logger.warning("No access points found, cannot test get_ap")
            return False
        
        # Get the first AP's ID and venue ID
        ap_serial = aps[0].get('serialNumber')
        venue_id = aps[0].get('venueId')
        
        if not (ap_serial and venue_id):
            logger.warning("AP data incomplete, cannot test get_ap")
            return False
        
        logger.info(f"Getting AP with Serial: {ap_serial}, Venue ID: {venue_id}")
        
        # Get the AP details
        ap = ap_module.get(venue_id, ap_serial)
        logger.info(f"Got AP: {ap.get('name')} (Serial: {ap.get('serialNumber')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            ap_module.get(venue_id, non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent AP ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_ap: {e}")
        return False

def test_get_ap_status(ap_module: AccessPoints):
    """Test getting an access point's status."""
    logger.info("Testing get_ap_status...")
    try:
        # First, get a list of APs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = ap_module.list(query_data)
        aps = result.get('data', [])
        
        if not aps:
            logger.warning("No access points found, cannot test get_ap_status")
            return False
        
        # Get the first AP's ID and venue ID
        ap_serial = aps[0].get('serialNumber')
        venue_id = aps[0].get('venueId')
        
        if not (ap_serial and venue_id):
            logger.warning("AP data incomplete, cannot test get_ap_status")
            return False
        
        logger.info(f"Getting status for AP with Serial: {ap_serial}, Venue ID: {venue_id}")
        
        # Get the AP status
        status = ap_module.get_status(venue_id, ap_serial)
        logger.info(f"Got AP status: {status.get('status', 'Unknown')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_ap_status: {e}")
        return False

def run_tests():
    """Run all access point module tests."""
    client = init_client()
    ap_module = AccessPoints(client)
    
    # Track test results
    results = {
        "list_aps": test_list_aps(ap_module),
        "get_ap": test_get_ap(ap_module),
        "get_ap_status": test_get_ap_status(ap_module)
    }
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_passed = False
        print(f"{test_name}: {status}")
    
    print("=" * 80)
    print(f"OVERALL: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)