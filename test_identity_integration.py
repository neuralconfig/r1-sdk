#!/usr/bin/env python3
"""
Integration test script for Identity Groups and Identities modules.

This script demonstrates how to use the identity management features of the RUCKUS One API.

Usage:
    python3 test_identity_integration.py
"""

import os
import sys
import logging
import configparser
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ruckus_one.client import RuckusOneClient

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
    """Run integration test."""
    # Initialize client
    config = load_config()
    client = RuckusOneClient(
        client_id=config.get('client_id', os.environ.get("RUCKUS_CLIENT_ID")),
        client_secret=config.get('client_secret', os.environ.get("RUCKUS_CLIENT_SECRET")),
        tenant_id=config.get('tenant_id', os.environ.get("RUCKUS_TENANT_ID")),
        region=config.get('region', 'na')
    )
    
    logger.info("Starting identity management integration test...")
    
    # 1. List existing identity groups
    logger.info("\n1. Listing identity groups:")
    groups = client.identity_groups.list()
    logger.info(f"   Found {len(groups.get('content', []))} identity groups")
    
    # 2. Create a test identity group
    logger.info("\n2. Creating a test identity group:")
    test_group = client.identity_groups.create(
        name=f"API Test Group {int(time.time())}",
        description="Test group created by integration test"
    )
    group_id = test_group.get('id')
    logger.info(f"   Created group: {test_group.get('name')} (ID: {group_id})")
    
    # 3. Create an identity in the group
    logger.info("\n3. Creating an identity in the group:")
    test_identity = client.identity_groups.create_identity(
        group_id=group_id,
        name=f"Test User {int(time.time())}",
        email="testuser@example.com",
        description="Test identity created by integration test"
    )
    identity_id = test_identity.get('id')
    logger.info(f"   Created identity: {test_identity.get('name')} (ID: {identity_id})")
    
    # 4. List all identities
    logger.info("\n4. Listing all identities:")
    all_identities = client.identities.list(page_size=5)
    logger.info(f"   Found {all_identities.get('totalElements', 0)} total identities")
    logger.info(f"   Showing first {len(all_identities.get('content', []))} identities")
    
    # 5. Query identities with filtering
    logger.info("\n5. Querying identities:")
    queried_identities = client.identities.query(page=0, page_size=10)
    logger.info(f"   Query returned {len(queried_identities.get('content', []))} identities")
    
    # 6. Get specific identity details
    logger.info("\n6. Getting specific identity details:")
    identity_details = client.identities.get(group_id, identity_id)
    logger.info(f"   Identity: {identity_details.get('name')}")
    logger.info(f"   Email: {identity_details.get('email')}")
    logger.info(f"   Device count: {identity_details.get('deviceCount', 0)}")
    
    # 7. Update the identity
    logger.info("\n7. Updating identity:")
    try:
        updated = client.identities.update(
            group_id=group_id,
            identity_id=identity_id,
            description="Updated description from integration test"
        )
        logger.info("   Identity updated successfully")
    except Exception as e:
        logger.warning(f"   Could not update identity: {e}")
    
    # 8. Add a device to the identity
    logger.info("\n8. Adding a device to the identity:")
    try:
        device_result = client.identities.add_device(
            group_id=group_id,
            identity_id=identity_id,
            mac_address="AA-BB-CC-DD-EE-FF",
            name="Test Device"
        )
        logger.info("   Device added successfully")
    except Exception as e:
        logger.warning(f"   Could not add device: {e}")
    
    # 9. Export identities to CSV
    logger.info("\n9. Exporting identities to CSV:")
    try:
        csv_data = client.identities.export_csv()
        logger.info(f"   Exported {len(csv_data)} bytes of CSV data")
    except Exception as e:
        logger.warning(f"   Could not export CSV: {e}")
    
    # 10. Clean up - delete the test identity and group
    logger.info("\n10. Cleaning up:")
    try:
        client.identities.delete(group_id, identity_id)
        logger.info("    Deleted test identity")
    except Exception as e:
        logger.warning(f"    Could not delete identity: {e}")
    
    try:
        client.identity_groups.delete(group_id)
        logger.info("    Deleted test group")
    except Exception as e:
        logger.warning(f"    Could not delete group: {e}")
    
    logger.info("\nIntegration test completed!")

if __name__ == "__main__":
    main()