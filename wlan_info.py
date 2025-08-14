#!/usr/bin/env python3
"""
Script to print WLAN information for debugging the inventory report.
"""

import os
import sys
import configparser
import json
from pprint import pprint

# Configure paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.wlans import WLANs

def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_path = os.path.join(script_dir, 'config.ini')
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
    # Load config
    config = load_config()
    
    # Initialize client
    client = RuckusOneClient(
        client_id=config.get('client_id'),
        client_secret=config.get('client_secret'),
        tenant_id=config.get('tenant_id'),
        region=config.get('region', 'na')
    )
    
    # Get WLANs
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    result = client.wlans.list(query_data)
    wlans = result.get('data', [])
    
    print(f"Found {len(wlans)} WLANs")
    print("\nSample of WLANs:")
    for i, wlan in enumerate(wlans[:5]):
        print(f"\nWLAN {i+1}:")
        print(f"  Name: {wlan.get('name')}")
        print(f"  SSID: {wlan.get('ssid')}")
        print(f"  ID: {wlan.get('id')}")
        print(f"  Venue ID: {wlan.get('venueId')}")
        
        # Print deployment information if available
        deployments = wlan.get('deployments', [])
        if deployments:
            print(f"  Deployments: {len(deployments)}")
            for j, deployment in enumerate(deployments[:3]):  # Limit to first 3 deployments
                print(f"    Deployment {j+1}: Type: {deployment.get('type')}, ID: {deployment.get('id')}")
        else:
            print("  Deployments: None")
        
        # Print venues information if available
        venues = wlan.get('venues', [])
        if venues:
            print(f"  Venues: {len(venues)}")
            for j, venue in enumerate(venues[:3]):  # Limit to first 3 venues
                print(f"    Venue {j+1}: ID: {venue.get('id')}, Name: {venue.get('name')}")
        else:
            print("  Venues: None")
    
    print("\nKeys available in WLAN object:")
    if wlans:
        print(list(wlans[0].keys()))
    
    # Example: look for WLANs in a specific venue (replace with actual venue ID)
    example_venue_id = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"  # Replace with your venue ID
    print(f"\nChecking for WLANs in example venue (ID: {example_venue_id}):")
    
    venue_wlans_count = 0
    
    print("\nWLANs with venueId matching example venue:")
    for wlan in wlans:
        if wlan.get('venueId') == example_venue_id:
            venue_wlans_count += 1
            print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')})")
    
    print(f"Count: {venue_wlans_count}")
    
    venue_wlans_count = 0
    print("\nWLANs with venues array containing Home:")
    for wlan in wlans:
        venues = wlan.get('venues', [])
        for venue in venues:
            if venue.get('id') == home_venue_id:
                venue_wlans_count += 1
                print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')})")
                break
    
    print(f"Count: {venue_wlans_count}")
    
    venue_wlans_count = 0
    print("\nWLANs with deployments containing Home:")
    for wlan in wlans:
        deployments = wlan.get('deployments', [])
        for deployment in deployments:
            if deployment.get('id') == home_venue_id:
                venue_wlans_count += 1
                print(f"  {wlan.get('name')} (SSID: {wlan.get('ssid')}) - Deployment type: {deployment.get('type')}")
                break
    
    print(f"Count: {venue_wlans_count}")
    
    print("\nChecking venue AP groups:")
    # Get venue AP groups for Home venue
    try:
        venue_result = client.venues.get(home_venue_id)
        print(f"Found venue: {venue_result.get('name')}")
        
        # Check for AP groups in the venue
        ap_groups = venue_result.get('apGroups', [])
        print(f"AP Groups in venue: {len(ap_groups)}")
        
        # Print AP group details
        for i, ap_group in enumerate(ap_groups):
            print(f"  AP Group {i+1}: ID: {ap_group.get('id')}, Name: {ap_group.get('name')}")
            
            # Now check for WLANs deployed to this AP group
            ap_group_id = ap_group.get('id')
            if ap_group_id:
                ap_group_wlans = 0
                for wlan in wlans:
                    deployments = wlan.get('deployments', [])
                    for deployment in deployments:
                        if deployment.get('type') == 'AP_GROUP' and deployment.get('id') == ap_group_id:
                            ap_group_wlans += 1
                            print(f"    WLAN: {wlan.get('name')} (SSID: {wlan.get('ssid')})")
                print(f"  Total WLANs in AP Group: {ap_group_wlans}")
        
        # Try to get more info about the venue and its WLANs
        print("\nAttempting direct API request for venue WLANs:")
        
        # Check if there's a specific venue_wlans endpoint
        home_id = home_venue_id
        direct_url = f"/venues/{home_id}/wifiNetworks"
        try:
            wifis_result = client.get(direct_url)
            if isinstance(wifis_result, dict) and 'data' in wifis_result:
                venue_wifis = wifis_result.get('data', [])
                print(f"Found {len(venue_wifis)} WLANs for venue via direct API")
                for wifi in venue_wifis[:10]:  # Show first 10 only
                    print(f"  WLAN: {wifi.get('name', 'Unnamed')} (SSID: {wifi.get('ssid', 'Unknown')})")
            else:
                print(f"Unexpected response format from {direct_url}")
        except Exception as e:
            print(f"Error querying {direct_url}: {e}")
        
        # Try query endpoint
        direct_url = f"/venues/{home_id}/wifiNetworks/query"
        query_data = {
            "pageSize": 100,
            "page": 0,
            "sortOrder": "ASC"
        }
        try:
            wifis_result = client.post(direct_url, data=query_data)
            if isinstance(wifis_result, dict) and 'data' in wifis_result:
                venue_wifis = wifis_result.get('data', [])
                print(f"Found {len(venue_wifis)} WLANs for venue via query API")
                for wifi in venue_wifis[:10]:  # Show first 10 only
                    print(f"  WLAN: {wifi.get('name', 'Unnamed')} (SSID: {wifi.get('ssid', 'Unknown')})")
                    print(f"  Status: {wifi.get('status', 'Unknown')}")
            else:
                print(f"Unexpected response format from {direct_url}")
        except Exception as e:
            print(f"Error querying {direct_url}: {e}")
            
        # Generate more extensive debug info for all WLANs
        print("\nExtensive WLAN Debug Info:")
        home_wlans = []
        for wlan in wlans:
            # Check if this WLAN has any reference to the Home venue
            wlan_name = wlan.get('name', '').lower()
            
            # Check various attributes for home references
            if 'home' in wlan_name or 'guest' in wlan_name or 'iot' in wlan_name:
                home_wlans.append(wlan)
                print(f"\nWLAN with name match: {wlan.get('name')} (SSID: {wlan.get('ssid')})")
                print(f"  Status: {wlan.get('status', 'Unknown')}")
                print(f"  Network Type: {wlan.get('nwType', 'Unknown')} / {wlan.get('nwSubType', 'Unknown')}")
                print(f"  Client Count: {wlan.get('clientCount', 'Unknown')}")
                print(f"  All Attributes: {list(wlan.keys())}")
                
        print(f"\nTotal Home-related WLANs found by name: {len(home_wlans)}")
    except Exception as e:
        print(f"Error checking venue AP groups: {e}")

if __name__ == "__main__":
    main()