#!/usr/bin/env python3
"""
Test script for the VLANs module of the RUCKUS One API.

This script tests various operations related to VLANs,
including listing VLANs, getting VLAN details, and other VLAN operations.

Usage:
    python test_vlans.py
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
from ruckus_one.modules.vlans import VLANs
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

def test_list_vlans(vlans_module: VLANs):
    """Test listing VLANs."""
    logger.info("Testing list_vlans...")
    try:
        # Test with default parameters
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = vlans_module.list(query_data)
        vlans = result.get('data', [])
        logger.info(f"Found {len(vlans)} VLANs")
        
        # Print first VLAN details
        if vlans:
            first_vlan = vlans[0]
            logger.info(f"First VLAN: {first_vlan.get('name')} (ID: {first_vlan.get('id')}, VLAN ID: {first_vlan.get('vlanId')})")
        
        # Test with pagination
        query_data_page = {
            "pageSize": 2,
            "page": 0,
            "sortOrder": "ASC"
        }
        result_page = vlans_module.list(query_data_page)
        vlans_page = result_page.get('data', [])
        logger.info(f"Found {len(vlans_page)} VLANs in first page")
        
        # Test with VLAN ID filtering (if available)
        if vlans:
            vlan_id = vlans[0].get('vlanId')
            if vlan_id:
                query_data_vlanid = {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC",
                    "filters": [
                        {
                            "type": "VLAN_ID",
                            "value": str(vlan_id)
                        }
                    ]
                }
                result_vlanid = vlans_module.list(query_data_vlanid)
                vlans_filtered = result_vlanid.get('data', [])
                logger.info(f"Found {len(vlans_filtered)} VLANs with VLAN ID {vlan_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_vlans: {e}")
        return False

def test_get_vlan(vlans_module: VLANs):
    """Test getting a VLAN by ID."""
    logger.info("Testing get_vlan...")
    try:
        # First, get a list of VLANs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = vlans_module.list(query_data)
        vlans = result.get('data', [])
        
        if not vlans:
            logger.warning("No VLANs found, cannot test get_vlan")
            return False
        
        # Get the first VLAN's ID
        vlan_id = vlans[0].get('id')
        
        if not vlan_id:
            logger.warning("VLAN data incomplete, cannot test get_vlan")
            return False
        
        logger.info(f"Getting VLAN with ID: {vlan_id}")
        
        # Get the VLAN details
        vlan = vlans_module.get(vlan_id)
        logger.info(f"Got VLAN: {vlan.get('name')} (ID: {vlan.get('id')}, VLAN ID: {vlan.get('vlanId')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            vlans_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent VLAN ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_vlan: {e}")
        return False

def test_get_venue_vlans(vlans_module: VLANs):
    """Test getting VLANs for a venue."""
    logger.info("Testing get_venue_vlans...")
    try:
        # First, get a list of VLANs
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = vlans_module.list(query_data)
        vlans = result.get('data', [])
        
        if not vlans:
            logger.warning("No VLANs found, cannot test get_venue_vlans")
            return False
        
        # Find a VLAN with a venue
        venue_id = None
        for vlan in vlans:
            # Check if this VLAN has a venue ID
            if vlan.get('venueId'):
                venue_id = vlan.get('venueId')
                break
        
        if not venue_id:
            logger.warning("No VLANs with venue ID found, cannot test get_venue_vlans")
            # Rather than fail, just don't test this function
            return True
        
        logger.info(f"Getting VLANs for venue with ID: {venue_id}")
        
        # Get the venue's VLANs
        query_data_venue = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        venue_vlans = vlans_module.get_venue_vlans(venue_id, query_data_venue)
        logger.info(f"Found {len(venue_vlans.get('data', []))} VLANs for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_vlans: {e}")
        return False

def run_tests():
    """Run all VLAN module tests."""
    client = init_client()
    vlans_module = VLANs(client)
    
    # Track test results
    results = {
        "list_vlans": test_list_vlans(vlans_module),
        "get_vlan": test_get_vlan(vlans_module),
        "get_venue_vlans": test_get_venue_vlans(vlans_module)
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