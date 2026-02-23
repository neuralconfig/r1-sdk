#!/usr/bin/env python3
"""
Test script for accessing and managing switch VLANs in the RUCKUS One SDK.
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
from ruckus_one.modules.switches import Switches

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
    """Main function to test switch VLANs."""
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
    switches_module = Switches(client)
    
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
    
    # List switches in the venue
    print("\nGetting switches in the venue...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    try:
        switches_result = switches_module.list(query_data)
        switches_list = switches_result.get('data', [])
        
        if not switches_list:
            print("No switches found in the venue.")
            return
        
        print(f"Found {len(switches_list)} switches:")
        for switch in switches_list:
            print(f"- {switch.get('name', 'Unknown')} (ID: {switch.get('id', 'Unknown')}, Serial: {switch.get('serialNumber', 'Unknown')})")
        
        # Get the first switch
        switch = switches_list[0]
        switch_id = switch.get('id')
        switch_serial = switch.get('serialNumber')
        switch_name = switch.get('name')
        print(f"\nUsing switch: {switch_name} (ID: {switch_id}, Serial: {switch_serial})")
        
        # Skip VLAN retrieval due to permissions
        print("\nSkipping direct VLAN retrieval due to permission limitations.")
        
        # Get switch ports
        print("\nGetting switch ports...")
        port_query = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        ports_result = switches_module.get_ports(port_query)
        ports_list = ports_result.get('data', [])
        
        print(f"Found {len(ports_list)} ports:")
        for port in ports_list:
            print(f"- Port {port.get('portId')}: {port.get('description', 'No description')} (VLAN: {port.get('pvid', 'N/A')})")
        
        # Print details of first port if available
        if ports_list:
            first_port = ports_list[0]
            print("\nDetails of the first port:")
            pprint(first_port)
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()