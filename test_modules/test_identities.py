#!/usr/bin/env python3
"""
Test script for the Identities module of the RUCKUS One API.

This script tests various operations related to identities across all groups,
including CRUD operations and device management.

Usage:
    python3 test_identities.py
"""

import os
import sys
import logging
import configparser
from typing import Dict, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.identities import Identities
from ruckus_one.modules.identity_groups import IdentityGroups
from ruckus_one.exceptions import ResourceNotFoundError, ValidationError

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

def test_list_identities(identities_module: Identities):
    """Test listing identities across all groups."""
    logger.info("Testing list_identities...")
    try:
        # Test with default parameters
        result = identities_module.list()
        
        if 'content' in result:
            identities = result['content']
            logger.info(f"Found {len(identities)} identities across all groups")
            
            # Print first few identities
            for i, identity in enumerate(identities[:3]):
                logger.info(f"Identity {i+1}: {identity.get('name', 'N/A')} (ID: {identity.get('id', 'N/A')})")
                logger.info(f"  Group: {identity.get('identityGroupName', 'N/A')}")
                logger.info(f"  Email: {identity.get('email', 'N/A')}")
        else:
            logger.info(f"Response keys: {list(result.keys())}")
        
        # Test with pagination
        result_page = identities_module.list(page=0, page_size=5)
        if 'content' in result_page:
            logger.info(f"Found {len(result_page['content'])} identities in first page")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_identities: {e}")
        return False

def test_query_identities(identities_module: Identities):
    """Test querying identities with filters."""
    logger.info("Testing query_identities...")
    try:
        # Test basic query
        result = identities_module.query(page=0, page_size=10)
        
        if 'content' in result:
            identities = result['content']
            logger.info(f"Query returned {len(identities)} identities")
            
            # Check pagination info
            logger.info(f"Total elements: {result.get('totalElements', 'N/A')}")
            logger.info(f"Total pages: {result.get('totalPages', 'N/A')}")
        else:
            logger.info(f"Response keys: {list(result.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing query_identities: {e}")
        return False

def test_get_identity(identities_module: Identities):
    """Test getting an identity by ID."""
    logger.info("Testing get_identity...")
    try:
        # First, get a list of identities
        result = identities_module.list()
        identities = result.get('content', [])
        
        if not identities:
            logger.warning("No identities found to test get operation")
            return False
        
        # Get the first identity's ID
        identity_id = identities[0].get('id')
        logger.info(f"Getting identity with ID: {identity_id}")
        
        # Get the identity details
        identity = identities_module.get(identity_id)
        logger.info(f"Retrieved identity: {identity.get('name')} (ID: {identity.get('id')})")
        logger.info(f"  Email: {identity.get('email', 'N/A')}")
        logger.info(f"  Device count: {identity.get('deviceCount', 0)}")
        
        # Test with non-existent ID
        try:
            non_existent_id = "00000000-0000-0000-0000-000000000000"
            identities_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent identity ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_identity: {e}")
        return False

def test_update_identity(identities_module: Identities):
    """Test updating an identity."""
    logger.info("Testing update_identity...")
    try:
        # First, get a list of identities
        result = identities_module.list()
        identities = result.get('content', [])
        
        if not identities:
            logger.warning("No identities found to test update operation")
            return False
        
        # Get the first identity
        identity_id = identities[0].get('id')
        original_description = identities[0].get('description', '')
        
        # Update the identity
        update_data = {
            "description": f"Updated by test script at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        result = identities_module.update(identity_id, **update_data)
        
        # Check if it's an async operation
        if 'requestId' in result:
            logger.info(f"Identity update initiated with request ID: {result['requestId']}")
        else:
            logger.info(f"Updated identity: {result.get('name')} with new description")
        
        return True
    except Exception as e:
        logger.error(f"Error testing update_identity: {e}")
        return False

def test_identity_devices(identities_module: Identities):
    """Test device operations for an identity."""
    logger.info("Testing identity_devices...")
    try:
        # First, get a list of identities
        result = identities_module.list()
        identities = result.get('content', [])
        
        if not identities:
            logger.warning("No identities found to test device operations")
            return False
        
        # Find an identity to work with
        identity_id = identities[0].get('id')
        logger.info(f"Testing device operations for identity: {identities[0].get('name')}")
        
        # Get current devices
        try:
            devices_result = identities_module.get_devices(identity_id)
            current_devices = devices_result.get('content', []) if isinstance(devices_result, dict) else []
            logger.info(f"Identity currently has {len(current_devices)} devices")
        except Exception as e:
            logger.warning(f"Could not get devices: {e}")
            current_devices = []
        
        # Test adding a device
        test_mac = f"AA-BB-CC-{int(time.time()) % 100:02d}-EE-FF"
        device_data = {
            "mac_address": test_mac,
            "name": "Test Device",
            "description": "Device added by test script"
        }
        
        try:
            result = identities_module.add_device(identity_id, **device_data)
            logger.info(f"Successfully added device with MAC: {test_mac}")
        except ValidationError as e:
            logger.error(f"Validation error adding device: {e}")
            return False
        except Exception as e:
            logger.warning(f"Could not add device: {e}")
        
        # Test invalid MAC address format
        try:
            invalid_mac = "AA:BB:CC:DD:EE:FF"  # Wrong format (colons instead of hyphens)
            identities_module.add_device(identity_id, mac_address=invalid_mac)
            logger.error("Expected ValidationError for invalid MAC format but got no exception")
            return False
        except ValidationError:
            logger.info("Correctly received ValidationError for invalid MAC address format")
        
        return True
    except Exception as e:
        logger.error(f"Error testing identity_devices: {e}")
        return False

def test_export_identities_csv(identities_module: Identities):
    """Test exporting identities to CSV."""
    logger.info("Testing export_identities_csv...")
    try:
        # Export identities to CSV
        csv_content = identities_module.export_csv()
        
        if csv_content:
            logger.info(f"Successfully exported identities to CSV (size: {len(csv_content)} bytes)")
            
            # Check if it looks like CSV content
            if csv_content.startswith(b'"') or csv_content.startswith(b'name') or b',' in csv_content[:100]:
                logger.info("CSV content appears to be valid")
            else:
                logger.warning("CSV content format may be unexpected")
        else:
            logger.warning("No CSV content returned")
        
        return True
    except Exception as e:
        logger.error(f"Error testing export_identities_csv: {e}")
        return False

def run_tests():
    """Run all identities module tests."""
    client = init_client()
    identities_module = Identities(client)
    
    # Track test results
    results = {}
    
    # Run tests
    results["list_identities"] = test_list_identities(identities_module)
    results["query_identities"] = test_query_identities(identities_module)
    results["get_identity"] = test_get_identity(identities_module)
    results["update_identity"] = test_update_identity(identities_module)
    results["identity_devices"] = test_identity_devices(identities_module)
    results["export_identities_csv"] = test_export_identities_csv(identities_module)
    
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