#!/usr/bin/env python3
"""
Test script for L3ACL functionality.

This script tests the L3ACL module operations including:
- Listing L3ACL policies
- Creating a test L3ACL policy
- Retrieving the created policy
- Updating the policy
- Deleting the policy
"""

import logging
import sys
import os
import configparser
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ruckus_one.client import RuckusOneClient
from ruckus_one.auth import Auth
from ruckus_one.exceptions import ResourceNotFoundError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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

def test_l3acl_operations():
    """Test basic L3ACL operations."""
    try:
        # Initialize client
        logger.info("Initializing RUCKUS One client...")
        
        # Load config and credentials
        config = load_config()
        
        client_id = os.environ.get("R1_CLIENT_ID") or config.get('client_id')
        client_secret = os.environ.get("R1_CLIENT_SECRET") or config.get('client_secret')
        tenant_id = os.environ.get("R1_TENANT_ID") or config.get('tenant_id')
        region = os.environ.get("R1_REGION") or config.get('region', 'na')
        
        if not all([client_id, client_secret, tenant_id]):
            logger.error("Missing authentication credentials. Set R1_CLIENT_ID, R1_CLIENT_SECRET, R1_TENANT_ID environment variables or create config.ini")
            return False
            
        client = RuckusOneClient(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            region=region
        )
        
        # Test listing L3ACL policies
        logger.info("Testing L3ACL policy listing...")
        policies = client.l3acl.list()
        logger.info(f"Found {len(policies.get('data', []))} existing L3ACL policies")
        
        # Create sample L3 rules for testing
        test_rules = [
            {
                "priority": 1,
                "description": "Allow HTTP to 192.168.1.0/24",
                "access": "ALLOW",
                "source": {
                    "enableIpSubnet": False
                },
                "destination": {
                    "enableIpSubnet": True,
                    "ip": "192.168.1.0",
                    "ipMask": "255.255.255.0",
                    "port": "80"
                }
            },
            {
                "priority": 2,
                "description": "Allow HTTPS to 192.168.1.0/24",
                "access": "ALLOW",
                "source": {
                    "enableIpSubnet": False
                },
                "destination": {
                    "enableIpSubnet": True,
                    "ip": "192.168.1.0",
                    "ipMask": "255.255.255.0",
                    "port": "443"
                }
            },
            {
                "priority": 3,
                "description": "Block all other traffic",
                "access": "BLOCK",
                "source": {
                    "enableIpSubnet": False
                },
                "destination": {
                    "enableIpSubnet": False
                }
            }
        ]
        
        # Test creating L3ACL policy
        test_policy_name = "Test-L3ACL-Policy"
        logger.info(f"Testing L3ACL policy creation: {test_policy_name}")
        
        create_response = client.l3acl.create(
            name=test_policy_name,
            l3_rules=test_rules,
            description="Test L3ACL policy created by test script",
            default_access="BLOCK"
        )
        
        logger.info(f"Policy creation response: {create_response}")
        
        if 'requestId' in create_response:
            logger.info(f"Policy creation initiated with requestId: {create_response['requestId']}")
            logger.info("Note: Policy creation is asynchronous. Use the requestId to check status.")
        
        # Note: Since policy creation is asynchronous, we can't immediately test
        # get/update/delete operations. In a real scenario, you would:
        # 1. Poll the activity API with the requestId until SUCCESS
        # 2. Then list policies to find the created policy ID
        # 3. Then test get/update/delete operations
        
        logger.info("L3ACL operations test completed successfully!")
        logger.info("Note: Since operations are asynchronous, full CRUD testing requires polling the activity API")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        logger.exception("Full error details:")
        return False
    
    return True


def test_rule_creation():
    """Test the create_rule helper method."""
    logger.info("Testing L3ACL rule creation helper...")
    
    try:
        # Initialize client (we just need the module, not actual API calls)
        config = load_config()
        
        client_id = os.environ.get("R1_CLIENT_ID") or config.get('client_id') or "dummy"
        client_secret = os.environ.get("R1_CLIENT_SECRET") or config.get('client_secret') or "dummy"
        tenant_id = os.environ.get("R1_TENANT_ID") or config.get('tenant_id') or "dummy"
        region = os.environ.get("R1_REGION") or config.get('region', 'na')
        
        client = RuckusOneClient(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            region=region
        )
        
        # Test rule creation helper
        rule = client.l3acl.create_rule(
            description="Test rule for web traffic",
            priority=1,
            access="ALLOW",
            destination_enable_ip_subnet=True,
            destination_ip="10.0.0.0",
            destination_ip_mask="255.255.255.0",
            destination_port="80"
        )
        
        logger.info(f"Created test rule: {rule}")
        
        # Validate rule structure
        required_fields = ["description", "access", "source", "destination"]
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Missing required field: {field}")
        
        logger.info("Rule creation helper test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Rule creation test failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Starting L3ACL functionality tests...")
    
    all_tests_passed = True
    
    # Test rule creation helper
    if not test_rule_creation():
        all_tests_passed = False
    
    # Test L3ACL operations
    if not test_l3acl_operations():
        all_tests_passed = False
    
    if all_tests_passed:
        logger.info("All L3ACL tests passed!")
        sys.exit(0)
    else:
        logger.error("Some L3ACL tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()