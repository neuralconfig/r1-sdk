#!/usr/bin/env python3
"""
Test script for the Switches module of the RUCKUS One API.

This script tests various operations related to network switches, including
listing switches, getting switch details, and accessing port information.

Usage:
    python test_switches.py
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
from ruckus_one.modules.switches import Switches
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

def test_list_switches(switches_module: Switches):
    """Test listing switches."""
    logger.info("Testing list_switches...")
    try:
        # Test with default parameters
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = switches_module.list(query_data)
        switches = result.get('data', [])
        logger.info(f"Found {len(switches)} switches")
        
        # Print first switch details
        if switches:
            first_switch = switches[0]
            logger.info(f"First switch: {first_switch.get('name')} (ID: {first_switch.get('id')})")
        
        # Test with pagination
        query_data_page = {
            "pageSize": 2,
            "page": 0,
            "sortOrder": "ASC"
        }
        result_page = switches_module.list(query_data_page)
        switches_page = result_page.get('data', [])
        logger.info(f"Found {len(switches_page)} switches in first page")
        
        # Test with venue filter (if available)
        if switches:
            venue_id = switches[0].get('venueId')
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
                result_venue = switches_module.list(query_data_venue)
                switches_venue = result_venue.get('data', [])
                logger.info(f"Found {len(switches_venue)} switches in venue {venue_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_switches: {e}")
        return False

def test_get_switch(switches_module: Switches):
    """Test getting a switch by ID."""
    logger.info("Testing get_switch...")
    try:
        # First, get a list of switches
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = switches_module.list(query_data)
        switches = result.get('data', [])
        
        if not switches:
            logger.warning("No switches found, cannot test get_switch")
            return False
        
        # Get the first switch's ID
        switch_id = switches[0].get('id')
        
        if not switch_id:
            logger.warning("Switch data incomplete, cannot test get_switch")
            return False
        
        logger.info(f"Getting switch with ID: {switch_id}")
        
        # Get the switch details
        switch = switches_module.get(switch_id)
        logger.info(f"Got switch: {switch.get('name')} (ID: {switch.get('id')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            switches_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent switch ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_switch: {e}")
        return False

def test_get_ports(switches_module: Switches):
    """Test getting switch ports."""
    logger.info("Testing get_ports...")
    try:
        # Test with default parameters
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = switches_module.get_ports(query_data)
        ports = result.get('data', [])
        logger.info(f"Found {len(ports)} switch ports")
        
        # Print first port details
        if ports:
            first_port = ports[0]
            logger.info(f"First port: {first_port.get('name')} (ID: {first_port.get('id')})")
        
        # Test with pagination
        query_data_page = {
            "pageSize": 2,
            "page": 0,
            "sortOrder": "ASC"
        }
        result_page = switches_module.get_ports(query_data_page)
        ports_page = result_page.get('data', [])
        logger.info(f"Found {len(ports_page)} switch ports in first page")
        
        # Test with switch filter (if available)
        if ports:
            switch_mac = ports[0].get('switchMac')
            if switch_mac:
                query_data_switch = {
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC",
                    "filters": [
                        {
                            "type": "SWITCH",
                            "value": switch_mac
                        }
                    ]
                }
                result_switch = switches_module.get_ports(query_data_switch)
                ports_switch = result_switch.get('data', [])
                logger.info(f"Found {len(ports_switch)} ports for switch {switch_mac}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_ports: {e}")
        return False

def test_get_port(switches_module: Switches):
    """Test getting a specific port."""
    logger.info("Testing get_port...")
    try:
        # First, get a list of ports
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        result = switches_module.get_ports(query_data)
        ports = result.get('data', [])
        
        if not ports:
            logger.warning("No ports found, cannot test get_port")
            return False
        
        # Get the first port's ID
        port_id = ports[0].get('id')
        
        if not port_id:
            logger.warning("Port data incomplete, cannot test get_port")
            return False
        
        logger.info(f"Getting port with ID: {port_id}")
        
        # Get the port details
        port = switches_module.get_port(port_id)
        logger.info(f"Got port: {port.get('name')} (ID: {port.get('id')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            switches_module.get_port(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent port ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_port: {e}")
        return False

def run_tests():
    """Run all switch module tests."""
    client = init_client()
    switches_module = Switches(client)
    
    # Track test results
    results = {
        "list_switches": test_list_switches(switches_module),
        "get_switch": test_get_switch(switches_module),
        "get_ports": test_get_ports(switches_module),
        "get_port": test_get_port(switches_module)
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