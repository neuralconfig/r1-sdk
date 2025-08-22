#!/usr/bin/env python3
"""
Test script for AP logs API endpoint in the RUCKUS One SDK.
Tests the /venues/{venue_id}/aps/{ap_id}/logs endpoint to retrieve AP support logs.
"""
import os
import sys
import json
import time
import logging
import configparser
from datetime import datetime
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Add the parent directory to the system path to import the ruckus_one package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient
from ruckus_one.modules.venues import Venues
from ruckus_one.modules.access_points import AccessPoints

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

def find_home_venue(venues_module):
    """Find the Home venue."""
    logger.info("Searching for Home venue...")
    venues_result = venues_module.list(page_size=100, page=0, sort_order="ASC")
    venues_list = venues_result.get('data', [])
    
    for venue in venues_list:
        if venue.get('name', '').lower() == 'home':
            logger.info(f"Found Home venue: {venue.get('name')} (ID: {venue.get('id')})")
            return venue
    
    logger.warning("Home venue not found, using first available venue")
    if venues_list:
        venue = venues_list[0]
        logger.info(f"Using venue: {venue.get('name')} (ID: {venue.get('id')})")
        return venue
    
    raise Exception("No venues found")

def find_office_ap(ap_module, venue_id):
    """Find an AP with 'office' in the name."""
    logger.info("Searching for Office AP...")
    query_data = {
        "pageSize": 100,
        "page": 0,
        "sortOrder": "ASC"
    }
    
    aps_result = ap_module.list(query_data)
    aps_list = aps_result.get('data', [])
    
    logger.info(f"Found {len(aps_list)} total APs")
    
    # Filter APs by venue_id and look for office AP
    venue_aps = []
    for ap in aps_list:
        # Check if AP belongs to our venue using venueId field
        ap_venue_id = ap.get('venueId')
        if ap_venue_id == venue_id:
            venue_aps.append(ap)
    
    logger.info(f"Found {len(venue_aps)} APs in the Home venue")
    
    # Debug: Print first few APs to see the structure
    if venue_aps:
        logger.info("Sample APs in venue:")
        for i, ap in enumerate(venue_aps[:3]):
            logger.info(f"  {i+1}. Name: {ap.get('name')}, Serial: {ap.get('serialNumber')}, MAC: {ap.get('apMac')}")
    
    # First try to find an AP with 'office' in the name
    for ap in venue_aps:
        ap_name = ap.get('name', '').lower()
        if 'office' in ap_name:
            logger.info(f"Found Office AP: {ap.get('name')} (Serial: {ap.get('serialNumber')})")
            return ap
    
    logger.warning("Office AP not found, using first available AP in venue")
    if venue_aps:
        ap = venue_aps[0]
        logger.info(f"Using AP: {ap.get('name')} (Serial: {ap.get('serialNumber')})")
        return ap
    
    # If no APs in the specific venue, use any AP
    logger.warning("No APs found in venue, using first available AP from all venues")
    if aps_list:
        ap = aps_list[0]
        logger.info(f"Using AP: {ap.get('name')} (Serial: {ap.get('serialNumber')}) from venue: {ap.get('venueId')}")
        return ap
    
    raise Exception("No APs found")

def test_ap_logs(client, venue_id, ap_id, max_retries=5, retry_delay=30):
    """Test the AP logs API endpoint with retry logic."""
    endpoint = f"/venues/{venue_id}/aps/{ap_id}/logs"
    logger.info(f"Testing AP logs endpoint: {endpoint}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} - Making request to logs endpoint...")
            response = client.request("GET", endpoint, raw_response=True)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.info("Successfully retrieved AP logs!")
                    return response_data
                except json.JSONDecodeError:
                    # Response might be binary data (log file)
                    logger.info("Response appears to be binary data (log file)")
                    return {
                        "content_type": response.headers.get('Content-Type'),
                        "content_length": len(response.content),
                        "content": response.content[:1000].decode('utf-8', errors='ignore')  # First 1000 chars
                    }
            elif response.status_code == 202:
                logger.info("Request accepted, log collection in progress...")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.warning("Max retries reached, log collection may still be in progress")
                    return {"status": "in_progress", "message": "Log collection taking longer than expected"}
            elif response.status_code == 404:
                logger.error("AP logs endpoint not found (404)")
                return {"error": "Endpoint not found", "status_code": 404}
            else:
                logger.error(f"Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    return {"error": error_data, "status_code": response.status_code}
                except:
                    return {"error": response.text, "status_code": response.status_code}
                    
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                raise

def save_response_to_file(response_data, venue_id, ap_id):
    """Save the response to a file for analysis."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ap_logs_response_{venue_id}_{ap_id}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(response_data, f, indent=2, default=str)
    
    logger.info(f"Response saved to: {filename}")
    return filename

def main():
    """Main function to test AP logs API."""
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
    ap_module = AccessPoints(client)
    
    try:
        # Find Home venue
        venue = find_home_venue(venues_module)
        venue_id = venue.get('id')
        
        # Find Office AP
        ap = find_office_ap(ap_module, venue_id)
        ap_serial = ap.get('serialNumber')
        
        print(f"\nTesting AP logs for:")
        print(f"Venue: {venue.get('name')} (ID: {venue_id})")
        print(f"AP: {ap.get('name')} (Serial: {ap_serial})")
        print(f"AP Model: {ap.get('model', 'Unknown')}")
        print(f"AP MAC: {ap.get('apMac', 'Unknown')}")
        
        # Test the logs endpoint
        print(f"\nTesting logs endpoint...")
        response_data = test_ap_logs(client, venue_id, ap_serial)
        
        # Save response to file
        filename = save_response_to_file(response_data, venue_id, ap_serial)
        
        # Display results
        print(f"\n=== AP Logs Response ===")
        pprint(response_data)
        print(f"\nResponse saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main()