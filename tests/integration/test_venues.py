#!/usr/bin/env python3
"""
Test script for the Venues module of the RUCKUS One API.

This script tests various operations related to venues, including
listing venues, getting venue details, and other venue operations.

Usage:
    python test_venues.py
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
from ruckus_one.modules.venues import Venues
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

def test_list_venues(venues_module: Venues):
    """Test listing venues."""
    logger.info("Testing list_venues...")
    try:
        # Test with default parameters
        result = venues_module.list()
        venues = result.get('data', [])
        logger.info(f"Found {len(venues)} venues")
        
        # Print first venue details
        if venues:
            first_venue = venues[0]
            logger.info(f"First venue: {first_venue.get('name')} (ID: {first_venue.get('id')})")
        
        # Test with pagination
        result_page = venues_module.list(page=0, page_size=2)
        venues_page = result_page.get('data', [])
        logger.info(f"Found {len(venues_page)} venues in first page")
        
        # Test with search string
        if venues:
            # Use first venue name as search string
            search_term = venues[0].get('name')
            result_search = venues_module.list(search_string=search_term)
            venues_search = result_search.get('data', [])
            logger.info(f"Found {len(venues_search)} venues matching '{search_term}'")
        
        # Test with sorting
        result_sorted = venues_module.list(sort_field="name", sort_order="ASC")
        venues_sorted = result_sorted.get('data', [])
        logger.info(f"Found {len(venues_sorted)} venues sorted by name")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_venues: {e}")
        return False

def test_get_venue(venues_module: Venues):
    """Test getting a venue by ID."""
    logger.info("Testing get_venue...")
    try:
        # First, get a list of venues
        result = venues_module.list()
        venues = result.get('data', [])
        
        if not venues:
            logger.warning("No venues found, cannot test get_venue")
            return False
        
        # Get the first venue's ID
        venue_id = venues[0].get('id')
        logger.info(f"Getting venue with ID: {venue_id}")
        
        # Get the venue details
        venue = venues_module.get(venue_id)
        logger.info(f"Got venue: {venue.get('name')} (ID: {venue.get('id')})")
        
        # Test with non-existent ID
        try:
            non_existent_id = "non-existent-id"
            venues_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent venue ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue: {e}")
        return False

def test_venue_aps(venues_module: Venues):
    """Test getting APs for a venue."""
    logger.info("Testing get_venue_aps...")
    try:
        # First, get a list of venues
        result = venues_module.list()
        venues = result.get('data', [])
        
        if not venues:
            logger.warning("No venues found, cannot test get_venue_aps")
            return False
        
        # Get the first venue's ID
        venue_id = venues[0].get('id')
        logger.info(f"Getting APs for venue with ID: {venue_id}")
        
        # Get the venue's APs
        aps = venues_module.get_aps(venue_id)
        logger.info(f"Found {len(aps.get('data', []))} APs for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_aps: {e}")
        return False

def test_venue_switches(venues_module: Venues):
    """Test getting switches for a venue."""
    logger.info("Testing get_venue_switches...")
    try:
        # First, get a list of venues
        result = venues_module.list()
        venues = result.get('data', [])
        
        if not venues:
            logger.warning("No venues found, cannot test get_venue_switches")
            return False
        
        # Get the first venue's ID
        venue_id = venues[0].get('id')
        logger.info(f"Getting switches for venue with ID: {venue_id}")
        
        # Get the venue's switches
        switches = venues_module.get_switches(venue_id)
        logger.info(f"Found {len(switches.get('data', []))} switches for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_switches: {e}")
        return False

def test_venue_wlans(venues_module: Venues):
    """Test getting WLANs for a venue."""
    logger.info("Testing get_venue_wlans...")
    try:
        # First, get a list of venues
        result = venues_module.list()
        venues = result.get('data', [])
        
        if not venues:
            logger.warning("No venues found, cannot test get_venue_wlans")
            return False
        
        # Get the first venue's ID
        venue_id = venues[0].get('id')
        logger.info(f"Getting WLANs for venue with ID: {venue_id}")
        
        # Get the venue's WLANs
        wlans = venues_module.get_wlans(venue_id)
        logger.info(f"Found {len(wlans.get('data', []))} WLANs for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_wlans: {e}")
        return False

def test_venue_clients(venues_module: Venues):
    """Test getting clients for a venue."""
    logger.info("Testing get_venue_clients...")
    try:
        # First, get a list of venues
        result = venues_module.list()
        venues = result.get('data', [])
        
        if not venues:
            logger.warning("No venues found, cannot test get_venue_clients")
            return False
        
        # Get the first venue's ID
        venue_id = venues[0].get('id')
        logger.info(f"Getting clients for venue with ID: {venue_id}")
        
        # Get the venue's clients
        clients = venues_module.get_clients(venue_id)
        logger.info(f"Found {len(clients.get('data', []))} clients for venue")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_venue_clients: {e}")
        return False

def run_tests():
    """Run all venue module tests."""
    client = init_client()
    venues_module = Venues(client)
    
    # Track test results
    results = {
        "list_venues": test_list_venues(venues_module),
        "get_venue": test_get_venue(venues_module),
        "get_venue_aps": test_venue_aps(venues_module),
        "get_venue_switches": test_venue_switches(venues_module),
        "get_venue_wlans": test_venue_wlans(venues_module),
        "get_venue_clients": test_venue_clients(venues_module)
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