#!/usr/bin/env python3
"""
Test script for DPSK (Dynamic Pre-Shared Key) functionality.

This script tests various DPSK operations including:
- Listing DPSK services
- Creating/updating DPSK pools
- Managing passphrases
- Device associations
"""

import json
import sys
import os
import configparser
from datetime import datetime, timedelta
from ruckus_one import RuckusOneClient


def test_dpsk_operations(client):
    """Test DPSK operations."""
    print("\n=== Testing DPSK Operations ===\n")
    
    # Enable debug logging temporarily
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # List existing DPSK services
    print("1. Listing DPSK services...")
    try:
        # Test with empty query first
        print("   Testing with empty query object...")
        response = client.post("/dpskServices/query", {})
        print(f"   Raw response type: {type(response)}")
        if isinstance(response, bytes):
            print(f"   Response bytes: {response[:200]}")
        else:
            print(f"   Response: {response}")
            
        services = client.dpsk.list_services()
        print(f"   Found {len(services)} DPSK services")
        
        for service in services[:3]:  # Show first 3
            print(f"   - {service.get('name')} (ID: {service.get('id')})")
            print(f"     Type: {service.get('expirationType', 'N/A')}")
            print(f"     Device Limit: {service.get('deviceCountLimit', 'Unlimited')}")
            print(f"     Passphrase Format: {service.get('passphraseFormat', 'N/A')}")
            
    except Exception as e:
        print(f"   Error listing DPSK services: {e}")
        import traceback
        traceback.print_exc()
        return
        
    # Get details of first service if available
    if services:
        print("\n2. Getting DPSK service details...")
        try:
            service_id = services[0]['id']
            service = client.dpsk.get_service(service_id)
            print(f"   Service: {service.get('name')}")
            print(f"   - ID: {service.get('id')}")
            print(f"   - Expiration Type: {service.get('expirationType')}")
            print(f"   - Device Count Limit: {service.get('deviceCountLimit', 'Unlimited')}")
            print(f"   - Passphrase Format: {service.get('passphraseFormat')}")
            print(f"   - Passphrase Length: {service.get('passphraseLength')}")
            
        except Exception as e:
            print(f"   Error getting service details: {e}")
            
    # Test passphrase operations
    if services:
        service_id = services[0]['id']
        print(f"\n3. Testing passphrase operations for service: {services[0]['name']}")
        
        # List passphrases
        print("   a. Listing passphrases...")
        try:
            passphrases = client.dpsk.list_passphrases(service_id)
            print(f"      Found {len(passphrases)} passphrases")
            
            for pp in passphrases[:3]:  # Show first 3
                print(f"      - User: {pp.get('username', pp.get('userName', 'N/A'))}")
                print(f"        Passphrase: {pp.get('passphrase', 'Hidden')}")
                print(f"        MAC: {pp.get('userMac', 'N/A')}")
                print(f"        Devices: {pp.get('numberOfDevices', len(pp.get('devices', [])))}")
                
        except Exception as e:
            print(f"      Error listing passphrases: {e}")
            
        # Get passphrase details if available
        if passphrases:
            print("\n   b. Getting passphrase details...")
            try:
                pp_id = passphrases[0]['id']
                passphrase = client.dpsk.get_passphrase(service_id, pp_id)
                print(f"      Passphrase ID: {passphrase.get('id')}")
                print(f"      - User: {passphrase.get('username', passphrase.get('userName'))}")
                print(f"      - Created: {passphrase.get('createdDate', passphrase.get('createdTime'))}")
                print(f"      - Expires: {passphrase.get('expirationDate', passphrase.get('expirationTime', 'Never'))}")
                
            except Exception as e:
                print(f"      Error getting passphrase details: {e}")
                
        # Test device operations
        if passphrases and passphrases[0].get('id'):
            pp_id = passphrases[0]['id']
            print("\n   c. Testing device operations...")
            
            try:
                devices = client.dpsk.list_devices(service_id, pp_id)
                print(f"      Found {len(devices)} devices")
                
                for device in devices:
                    print(f"      - MAC: {device.get('mac')}")
                    print(f"        Name: {device.get('name', 'N/A')}")
                    
            except Exception as e:
                print(f"      Error listing devices: {e}")
                
    # Test DPSK service creation (commented out to avoid creating test data)
    """
    print("\n4. Creating test DPSK service...")
    try:
        test_service = client.dpsk.create_service(
            name=f"Test_DPSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Test DPSK service created by API test",
            type="SINGLE",
            maxPassphrases=100,
            maxDevicesPerPassphrase=5
        )
        print(f"   Created service: {test_service.get('name')} (ID: {test_service.get('id')})")
        
        # Clean up - delete the test service
        client.dpsk.delete_service(test_service['id'])
        print("   Cleaned up test service")
        
    except Exception as e:
        print(f"   Error creating test service: {e}")
    """
    
    # Test CSV export
    if services:
        print("\n5. Testing CSV export...")
        try:
            csv_data = client.dpsk.export_passphrases_csv(
                services[0]['id'],
                filters={"limit": 10}
            )
            print("   Successfully exported passphrases to CSV")
            print(f"   CSV preview (first 200 chars): {csv_data[:200]}...")
            
        except Exception as e:
            print(f"   Error exporting CSV: {e}")


def load_config():
    """Load configuration from config.ini file."""
    config = configparser.ConfigParser()
    config_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config-safe.ini'),
        'config.ini',
        'config-safe.ini'
    ]
    
    for config_path in config_paths:
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
    """Main test function."""
    print("RUCKUS One DPSK API Test")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Get credentials from environment or config
    client_id = os.environ.get("R1_CLIENT_ID") or config.get('client_id')
    client_secret = os.environ.get("R1_CLIENT_SECRET") or config.get('client_secret')
    tenant_id = os.environ.get("R1_TENANT_ID") or config.get('tenant_id')
    region = os.environ.get("R1_REGION") or config.get('region', 'na')
    
    # Initialize client
    try:
        if client_id and client_secret and tenant_id:
            client = RuckusOneClient(
                client_id=client_id,
                client_secret=client_secret,
                tenant_id=tenant_id,
                region=region
            )
        else:
            client = RuckusOneClient()
        print("✓ Client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize client: {e}")
        print("\nMake sure you have configured authentication:")
        print("- Set environment variables: R1_CLIENT_ID, R1_CLIENT_SECRET, R1_TENANT_ID")
        print("- Or create a config.ini file with [credentials] section")
        sys.exit(1)
        
    # Test DPSK operations
    test_dpsk_operations(client)
    
    print("\n" + "=" * 50)
    print("DPSK API test completed")


if __name__ == "__main__":
    main()