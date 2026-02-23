#!/usr/bin/env python3
"""
Quick test script to list identity groups using the RUCKUS One API.
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

def test_list_identity_groups(client: RuckusOneClient):
    """Test listing identity groups."""
    logger.info("Testing list identity groups...")
    
    try:
        # Method 1: Simple GET request
        logger.info("Method 1: Using GET /identityGroups")
        response = client.get("/identityGroups")
        logger.info(f"Response type: {type(response)}")
        
        if isinstance(response, dict):
            # Check if response has 'content' field (based on API doc)
            if 'content' in response:
                groups = response['content']
                logger.info(f"Found {len(groups)} identity groups")
                
                # Print first few groups
                for i, group in enumerate(groups[:3]):
                    logger.info(f"Group {i+1}: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
            else:
                logger.info(f"Response keys: {list(response.keys())}")
                logger.info(f"Full response: {response}")
        else:
            logger.info(f"Response: {response}")
            
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")
        
    try:
        # Method 2: Using POST query endpoint
        logger.info("\nMethod 2: Using POST /identityGroups/query")
        query_data = {
            "page": 0,
            "pageSize": 10
        }
        response = client.post("/identityGroups/query", data=query_data)
        logger.info(f"Response type: {type(response)}")
        
        if isinstance(response, dict):
            logger.info(f"Response keys: {list(response.keys())}")
            
            # Check different possible response structures
            if 'content' in response:
                groups = response['content']
                logger.info(f"Found {len(groups)} identity groups")
                
                # Print first few groups
                for i, group in enumerate(groups[:3]):
                    logger.info(f"Group {i+1}: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
            elif 'data' in response:
                groups = response['data']
                logger.info(f"Found {len(groups)} identity groups")
                
                # Print first few groups
                for i, group in enumerate(groups[:3]):
                    logger.info(f"Group {i+1}: {group.get('name', 'N/A')} (ID: {group.get('id', 'N/A')})")
            else:
                logger.info(f"Full response: {response}")
        else:
            logger.info(f"Response: {response}")
            
    except Exception as e:
        logger.error(f"Method 2 failed: {e}")

def main():
    """Main function."""
    client = init_client()
    test_list_identity_groups(client)

if __name__ == "__main__":
    main()