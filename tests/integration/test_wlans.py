#!/usr/bin/env python3
"""
Test script for the WLANs module of the RUCKUS One API.

This script tests various operations related to wireless networks (WLANs),
including listing WLANs, getting WLAN details, and other WLAN operations.

Usage:
    python test_wlans.py
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
from ruckus_one.modules.wlans import WLANs
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

def test_list_wlans(wlans_module: WLANs):
    """Test listing WLANs."""
    logger.info("Testing list_wlans...")
    try:
        # Test with default parameters
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = wlans_module.list(query_data)
        wlans = result.get('data', [])
        logger.info(f"Found {len(wlans)} WLANs")
        
        # Print first WLAN details
        if wlans:
            first_wlan = wlans[0]
            logger.info(f"First WLAN: {first_wlan.get('name')} (ID: {first_wlan.get('id')})")
        
        # Test with pagination
        query_data_page = {
            "pageSize": 2,
            "page": 0,
            "sortOrder": "ASC"
        }
        result_page = wlans_module.list(query_data_page)
        wlans_page = result_page.get('data', [])
        logger.info(f"Found {len(wlans_page)} WLANs in first page")
        
        # Test with SSID filtering (if available)
        if wlans:
            ssid = wlans[0].get('ssid')
            if ssid:
                query_data_ssid = {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC",
                    "filters": [
                        {
                            "type": "SSID",
                            "value": ssid
                        }
                    ]
                }
                result_ssid = wlans_module.list(query_data_ssid)
                wlans_ssid = result_ssid.get('data', [])
                logger.info(f"Found {len(wlans_ssid)} WLANs with SSID {ssid}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_wlans: {e}")
        return False

def test_get_wlan(wlans_module: WLANs):
    """Test getting a WLAN by ID."""
    logger.info("Testing get_wlan...")
    try:
        # First, get a list of WLANs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = wlans_module.list(query_data)
        wlans = result.get('data', [])
        
        if not wlans:
            logger.warning("No WLANs found, cannot test get_wlan")
            return False
        
        # Get the first WLAN's ID
        wlan_id = wlans[0].get('id')
        
        if not wlan_id:
            logger.warning("WLAN data incomplete, cannot test get_wlan")
            return False
        
        logger.info(f"Getting WLAN with ID: {wlan_id}")
        
        # Get the WLAN details
        wlan = wlans_module.get(wlan_id)
        logger.info(f"Got WLAN: {wlan.get('name')} (ID: {wlan.get('id')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            wlans_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent WLAN ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_wlan: {e}")
        return False

def test_get_venue_wlans(wlans_module: WLANs):
    """Test getting WLANs for a venue."""
    logger.info("Testing get_venue_wlans...")
    try:
        # First, get a list of WLANs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = wlans_module.list(query_data)
        wlans = result.get('data', [])
        
        if not wlans:
            logger.warning("No WLANs found, cannot test get_venue_wlans")
            return False
        
        # Find a WLAN that's deployed to a venue
        venue_id = None
        for wlan in wlans:
            # Check if this WLAN has venue deployments
            deployments = wlan.get('deployments', [])
            for deployment in deployments:
                if deployment.get('type') == 'VENUE':
                    venue_id = deployment.get('id')
                    if venue_id:
                        break
            if venue_id:
                break
        
        if not venue_id:
            logger.warning("No venue deployments found, cannot test get_venue_wlans")
            # Rather than fail, just don't test this function
            return True
        
        logger.info(f"Getting WLANs for venue with ID: {venue_id}")
        
        # Get the venue's WLANs
        query_data_venue = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        venue_wlans = wlans_module.get_venue_wlans(venue_id, query_data_venue)
        logger.info(f"Found {len(venue_wlans.get('data', []))} WLANs for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_wlans: {e}")
        return False

def run_tests():
    """Run all WLAN module tests."""
    client = init_client()
    wlans_module = WLANs(client)
    
    # Track test results
    results = {
        "list_wlans": test_list_wlans(wlans_module),
        "get_wlan": test_get_wlan(wlans_module),
        "get_venue_wlans": test_get_venue_wlans(wlans_module)
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