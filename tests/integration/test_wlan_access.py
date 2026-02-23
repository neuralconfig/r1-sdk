#!/usr/bin/env python3
"""
Test script for accessing WLAN (Wi-Fi network) information in the RUCKUS One SDK.
"""
import os
import sys
import logging
import configparser
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.venues import Venues
from ruckus_one.modules.wlans import WLANs

def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
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

def main():
    """Main function to test WLAN access."""
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
    print(f"Initializing client with region: {region}")
    client = RuckusOneClient(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id, region=region)
    
    # Initialize modules
    venues_module = Venues(client)
    wlan_module = WLANs(client)
    
    # Get venues
    print("Getting venues...")
    venues_result = venues_module.list()
    venues_list = venues_result.get('data', [])
    
    if not venues_list:
        print("No venues found.")
        return
    
    # Get the first venue
    venue = venues_list[0]
    venue_id = venue.get('id')
    venue_name = venue.get('name')
    print(f"\nUsing venue: {venue_name} (ID: {venue_id})")
    
    # Get WLANs in the venue
    print("\nGetting WLANs in the venue...")
    try:
        # Use the general WLAN query endpoint with simple parameters
        query_data = {
            "pageSize": 100,
            "page": 0
        }
        wlans_result = wlan_module.list(query_data)
        wlans_list = wlans_result.get('data', [])
        
        print(f"Found {len(wlans_list)} WLANs:")
        for wlan in wlans_list:
            print(f"- {wlan.get('name', 'Unknown')} (ID: {wlan.get('id', 'Unknown')}, SSID: {wlan.get('ssid', 'Unknown')})")
        
        # Print the first WLAN details
        if wlans_list:
            print("\nDetails of the first WLAN:")
            pprint(wlans_list[0])
        
    except Exception as e:
        print(f"Error getting WLANs: {e}")
        raise

if __name__ == "__main__":
    main()