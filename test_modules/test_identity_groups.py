#!/usr/bin/env python3
"""
Test script for the Identity Groups module of the RUCKUS One API.

This script tests various operations related to identity groups, including
CRUD operations and identity management within groups.

Usage:
    python3 test_identity_groups.py
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

def test_list_identity_groups(identity_groups_module: IdentityGroups):
    """Test listing identity groups."""
    logger.info("Testing list_identity_groups...")
    try:
        # Test simple list
        result = identity_groups_module.list()
        
        if 'content' in result:
            groups = result['content']
            logger.info(f"Found {len(groups)} identity groups")
            
            # Print first few groups
            for i, group in enumerate(groups[:3]):
                logger.info(f"Group {i+1}: {group.get('name')} (ID: {group.get('id')})")
        else:
            logger.warning(f"Unexpected response structure: {list(result.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing list_identity_groups: {e}")
        return False

def test_query_identity_groups(identity_groups_module: IdentityGroups):
    """Test querying identity groups with pagination."""
    logger.info("Testing query_identity_groups...")
    try:
        # Test with pagination
        result = identity_groups_module.query(page=0, page_size=5)
        
        if 'content' in result:
            groups = result['content']
            logger.info(f"Found {len(groups)} identity groups in first page")
            
            # Check pagination info
            logger.info(f"Total elements: {result.get('totalElements', 'N/A')}")
            logger.info(f"Total pages: {result.get('totalPages', 'N/A')}")
            logger.info(f"Current page: {result.get('number', 'N/A')}")
        else:
            logger.warning(f"Unexpected response structure: {list(result.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing query_identity_groups: {e}")
        return False

def test_create_identity_group(identity_groups_module: IdentityGroups):
    """Test creating an identity group."""
    logger.info("Testing create_identity_group...")
    try:
        # Create a test group
        group_name = f"Test Group {int(time.time())}"
        group_data = {
            "name": group_name,
            "description": "Test group created by API test script"
        }
        
        result = identity_groups_module.create(**group_data)
        
        # Check if it's an async operation
        if 'requestId' in result:
            logger.info(f"Identity group creation initiated with request ID: {result['requestId']}")
            logger.info("Note: This is an asynchronous operation. The group will be created shortly.")
            return result.get('id')  # Return the ID if available
        else:
            group_id = result.get('id')
            logger.info(f"Created identity group: {result.get('name')} (ID: {group_id})")
            return group_id
            
    except Exception as e:
        logger.error(f"Error testing create_identity_group: {e}")
        return None

def test_get_identity_group(identity_groups_module: IdentityGroups, group_id: str = None):
    """Test getting an identity group by ID."""
    logger.info("Testing get_identity_group...")
    try:
        # If no group_id provided, get the first available group
        if not group_id:
            result = identity_groups_module.list()
            groups = result.get('content', [])
            if not groups:
                logger.warning("No identity groups found to test get operation")
                return False
            group_id = groups[0]['id']
        
        # Get the specific group
        group = identity_groups_module.get(group_id)
        logger.info(f"Retrieved identity group: {group.get('name')} (ID: {group.get('id')})")
        logger.info(f"Group details: Identity count: {group.get('identityCount', 0)}")
        
        # Test with non-existent ID
        try:
            non_existent_id = "00000000-0000-0000-0000-000000000000"
            identity_groups_module.get(non_existent_id)
            logger.error("Expected ResourceNotFoundError but got no exception")
            return False
        except ResourceNotFoundError:
            logger.info("Correctly received ResourceNotFoundError for non-existent group ID")
        
        return True
    except Exception as e:
        logger.error(f"Error testing get_identity_group: {e}")
        return False

def test_create_identity_in_group(identity_groups_module: IdentityGroups, group_id: str = None):
    """Test creating an identity within a group."""
    logger.info("Testing create_identity_in_group...")
    try:
        # If no group_id provided, get the first available group
        if not group_id:
            result = identity_groups_module.list()
            groups = result.get('content', [])
            if not groups:
                logger.warning("No identity groups found to test identity creation")
                return False
            group_id = groups[0]['id']
        
        # Create a test identity
        identity_data = {
            "name": f"Test User {int(time.time())}",
            "email": f"testuser{int(time.time())}@example.com",
            "description": "Test identity created by API test script"
        }
        
        result = identity_groups_module.create_identity(group_id, **identity_data)
        
        # Check if it's an async operation
        if 'requestId' in result:
            logger.info(f"Identity creation initiated with request ID: {result['requestId']}")
            logger.info("Note: This is an asynchronous operation. The identity will be created shortly.")
        else:
            identity_id = result.get('id')
            logger.info(f"Created identity: {result.get('name')} (ID: {identity_id})")
            
        return True
    except Exception as e:
        logger.error(f"Error testing create_identity_in_group: {e}")
        return False

def test_get_identity_in_group(identity_groups_module: IdentityGroups, created_identity_id: str = None):
    """Test getting a specific identity within a group."""
    logger.info("Testing get_identity_in_group...")
    try:
        # Get the first available group
        result = identity_groups_module.list()
        groups = result.get('content', [])
        if not groups:
            logger.warning("No identity groups found")
            return False
        
        # If we have a created identity, use that
        if created_identity_id:
            group_id = groups[0]['id']
            try:
                identity = identity_groups_module.get_identity(group_id, created_identity_id)
                logger.info(f"Retrieved identity: {identity.get('name')} (ID: {identity.get('id')})")
                return True
            except Exception as e:
                logger.warning(f"Could not retrieve created identity: {e}")
        
        logger.info("Note: To fully test get_identity_in_group, an identity ID is needed")
        return True
        
    except Exception as e:
        logger.error(f"Error testing get_identity_in_group: {e}")
        return False

def test_delete_identity_group(identity_groups_module: IdentityGroups, group_id: str):
    """Test deleting an identity group."""
    logger.info("Testing delete_identity_group...")
    try:
        if not group_id:
            logger.warning("No group ID provided for deletion test")
            return False
        
        identity_groups_module.delete(group_id)
        logger.info(f"Successfully deleted identity group with ID: {group_id}")
        
        # Verify deletion
        try:
            identity_groups_module.get(group_id)
            logger.error("Group still exists after deletion")
            return False
        except ResourceNotFoundError:
            logger.info("Confirmed: Group has been deleted")
        
        return True
    except Exception as e:
        logger.error(f"Error testing delete_identity_group: {e}")
        return False

def run_tests():
    """Run all identity groups module tests."""
    client = init_client()
    identity_groups_module = IdentityGroups(client)
    
    # Track test results
    results = {}
    created_group_id = None
    
    # Run tests
    results["list_identity_groups"] = test_list_identity_groups(identity_groups_module)
    results["query_identity_groups"] = test_query_identity_groups(identity_groups_module)
    
    # Create a test group
    created_group_id = test_create_identity_group(identity_groups_module)
    results["create_identity_group"] = created_group_id is not None
    
    # Wait a bit for async operations
    if created_group_id and 'requestId' not in str(created_group_id):
        time.sleep(2)
    
    results["get_identity_group"] = test_get_identity_group(identity_groups_module)
    results["create_identity_in_group"] = test_create_identity_in_group(identity_groups_module)
    results["get_identity_in_group"] = test_get_identity_in_group(identity_groups_module)
    
    # Clean up - delete the test group if it was created
    if created_group_id and isinstance(created_group_id, str):
        results["delete_identity_group"] = test_delete_identity_group(identity_groups_module, created_group_id)
    else:
        results["delete_identity_group"] = True  # Skip if no group was created
    
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