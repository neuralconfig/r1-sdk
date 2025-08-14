#!/usr/bin/env python3
"""
L3 ACL CSV Import Script

This script imports CSV data containing IP address ranges and ports,
and creates a Layer-3 ACL policy in RUCKUS One. Each row in the CSV
represents a destination subnet and port that should be allowed.
A deny-all rule is added at the end.

Usage:
    python import_l3acl_csv.py --csv-file data/MS-endpoints.csv --policy-name "Microsoft-Endpoints-ACL"
"""

import argparse
import csv
import logging
import sys
import os
import configparser
from pathlib import Path
from typing import List, Dict, Any, Tuple
import ipaddress

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ruckus_one.client import RuckusOneClient
from ruckus_one.auth import Auth
from ruckus_one.modules.l3acl import MAX_L3ACL_RULES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_csv_file(csv_file_path: str) -> List[Tuple[str, str]]:
    """
    Parse CSV file and extract IP address ranges and ports.
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        List of tuples containing (ip_range, port)
    """
    entries = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since CSV has header
            # Handle different possible column names
            ip_range = None
            port = None
            
            # Try common column name variations
            for key in row.keys():
                key_lower = key.lower().strip()
                if 'ip' in key_lower or 'address' in key_lower or 'range' in key_lower:
                    ip_range = row[key].strip()
                elif 'port' in key_lower:
                    port = row[key].strip()
            
            if not ip_range or not port:
                logger.warning(f"Row {row_num}: Missing IP range or port data: {row}")
                continue
                
            # Validate IP range format
            try:
                ipaddress.ip_network(ip_range, strict=False)
            except ValueError as e:
                logger.warning(f"Row {row_num}: Invalid IP range '{ip_range}': {e}")
                continue
            
            # Validate port
            try:
                port_int = int(port)
                if not (1 <= port_int <= 65535):
                    raise ValueError("Port out of range")
            except ValueError as e:
                logger.warning(f"Row {row_num}: Invalid port '{port}': {e}")
                continue
                
            entries.append((ip_range, port))
            
    logger.info(f"Successfully parsed {len(entries)} valid entries from {csv_file_path}")
    return entries


def create_l3_rules(csv_entries: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    """
    Create L3 ACL rules from CSV entries.
    
    Args:
        csv_entries: List of (ip_range, port) tuples
        
    Returns:
        List of L3 rule dictionaries
    """
    rules = []
    
    # Create allow rules for each CSV entry
    for i, (ip_range, port) in enumerate(csv_entries, start=1):
        # Parse the network to get address and mask
        network = ipaddress.ip_network(ip_range, strict=False)
        network_address = str(network.network_address)
        netmask = str(network.netmask)
        
        rule = {
            "priority": i,
            "description": f"Allow traffic to {ip_range}:{port}",
            "access": "ALLOW",
            "source": {
                "enableIpSubnet": False
            },
            "destination": {
                "enableIpSubnet": True,
                "ip": network_address,
                "ipMask": netmask,
                "port": port
            }
        }
        
        rules.append(rule)
        
        if i % 50 == 0:  # Log progress every 50 rules
            logger.info(f"Created {i} rules...")
    
    logger.info(f"Created {len(rules)} total rules ({len(csv_entries)} allow rules)")
    logger.info("Note: Policy will use defaultAccess='BLOCK' to deny all other traffic")
    return rules


def create_l3acl_policies(client: RuckusOneClient, 
                         policy_name: str, 
                         csv_entries: List[Tuple[str, str]], 
                         description: str = None,
                         split_policies: bool = False) -> List[Dict[str, Any]]:
    """
    Create L3 ACL policy(ies) using the RUCKUS One API.
    
    Args:
        client: RUCKUS One API client
        policy_name: Base name for the L3 ACL policy
        csv_entries: List of (ip_range, port) tuples
        description: Optional description
        split_policies: Whether to split into multiple policies if too many rules
        
    Returns:
        List of API responses from policy creation
        
    Raises:
        ValueError: If too many rules and split_policies is False
    """
    total_rules = len(csv_entries)
    
    if total_rules > MAX_L3ACL_RULES and not split_policies:
        raise ValueError(
            f"CSV contains {total_rules} entries, but L3 ACL policies are limited to {MAX_L3ACL_RULES} rules. "
            f"Use --split-policies to automatically create multiple policies, or reduce the CSV to {MAX_L3ACL_RULES} entries."
        )
    
    # Calculate how many policies we need
    if total_rules <= MAX_L3ACL_RULES:
        # Single policy
        rules = create_l3_rules(csv_entries)
        if not description:
            description = f"L3 ACL policy created from CSV import with {len(rules)} allow rules"
        
        logger.info(f"Creating L3 ACL policy '{policy_name}' with {len(rules)} rules...")
        
        response = client.l3acl.create(
            name=policy_name,
            l3_rules=rules,
            description=description,
            default_access="BLOCK"
        )
        
        logger.info(f"Successfully created L3 ACL policy. Response: {response}")
        return [response]
    
    else:
        # Multiple policies needed
        policies_created = []
        num_policies = (total_rules + MAX_L3ACL_RULES - 1) // MAX_L3ACL_RULES  # Ceiling division
        
        logger.info(f"Splitting {total_rules} rules into {num_policies} policies...")
        
        for policy_num in range(num_policies):
            start_idx = policy_num * MAX_L3ACL_RULES
            end_idx = min(start_idx + MAX_L3ACL_RULES, total_rules)
            
            policy_csv_entries = csv_entries[start_idx:end_idx]
            rules = create_l3_rules(policy_csv_entries)
            
            # Create policy name with suffix
            if num_policies > 1:
                current_policy_name = f"{policy_name}-{policy_num + 1}"
            else:
                current_policy_name = policy_name
            
            current_description = description or f"L3 ACL policy created from CSV import (part {policy_num + 1} of {num_policies}) with {len(rules)} allow rules"
            
            logger.info(f"Creating L3 ACL policy '{current_policy_name}' with {len(rules)} rules (entries {start_idx + 1}-{end_idx})...")
            
            try:
                response = client.l3acl.create(
                    name=current_policy_name,
                    l3_rules=rules,
                    description=current_description,
                    default_access="BLOCK"
                )
                
                policies_created.append(response)
                logger.info(f"Successfully created L3 ACL policy '{current_policy_name}'")
                
            except Exception as e:
                logger.error(f"Failed to create L3 ACL policy '{current_policy_name}': {e}")
                raise
        
        logger.info(f"Successfully created {len(policies_created)} L3 ACL policies")
        return policies_created


def main():
    """Main function to handle command line arguments and orchestrate the import."""
    parser = argparse.ArgumentParser(
        description="Import CSV file and create L3 ACL policy in RUCKUS One",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Import with explicit config file
    python import_l3acl_csv.py --csv-file data/MS-endpoints.csv --policy-name "MS-Endpoints" --config config.ini
    
    # Import large CSV by splitting into multiple policies  
    python import_l3acl_csv.py --csv-file data/MS-endpoints.csv --policy-name "MS-Endpoints" --split-policies
    
    # Import using environment variables for auth
    export R1_CLIENT_ID="your-client-id"
    export R1_CLIENT_SECRET="your-client-secret" 
    export R1_TENANT_ID="your-tenant-id"
    python import_l3acl_csv.py --csv-file data/MS-endpoints.csv --policy-name "MS-Endpoints"
        """
    )
    
    parser.add_argument(
        '--csv-file',
        required=True,
        help='Path to CSV file containing IP ranges and ports'
    )
    
    parser.add_argument(
        '--policy-name',
        required=True,
        help='Name for the L3 ACL policy to create'
    )
    
    parser.add_argument(
        '--description',
        help='Description for the L3 ACL policy'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file (default: config.ini)',
        default='config.ini'
    )
    
    parser.add_argument(
        '--region',
        choices=['na', 'eu', 'asia'],
        default='na',
        help='RUCKUS One region (default: na)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse CSV and generate rules but do not create the policy'
    )
    
    parser.add_argument(
        '--split-policies',
        action='store_true',
        help=f'Automatically split large CSV files into multiple policies (max {MAX_L3ACL_RULES} rules per policy)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate CSV file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    try:
        # Parse CSV file
        logger.info(f"Parsing CSV file: {csv_path}")
        csv_entries = parse_csv_file(str(csv_path))
        
        if not csv_entries:
            logger.error("No valid entries found in CSV file")
            sys.exit(1)
        
        # Check rule count and provide guidance
        total_rules = len(csv_entries)
        if total_rules > MAX_L3ACL_RULES:
            if not args.split_policies and not args.dry_run:
                logger.error(f"CSV contains {total_rules} entries, but L3 ACL policies are limited to {MAX_L3ACL_RULES} rules.")
                logger.error(f"Options:")
                logger.error(f"  1. Use --split-policies to create multiple policies automatically")
                logger.error(f"  2. Reduce your CSV to {MAX_L3ACL_RULES} entries or fewer")
                logger.error(f"  3. Use --dry-run to see what would be created")
                sys.exit(1)
            elif args.split_policies:
                num_policies = (total_rules + MAX_L3ACL_RULES - 1) // MAX_L3ACL_RULES
                logger.info(f"CSV has {total_rules} entries. Will create {num_policies} policies with max {MAX_L3ACL_RULES} rules each.")
        
        if args.dry_run:
            # Create rules for dry run analysis
            if total_rules <= MAX_L3ACL_RULES:
                rules = create_l3_rules(csv_entries)
                logger.info("DRY RUN: Would create the following policy:")
                logger.info(f"  Name: {args.policy_name}")
                logger.info(f"  Description: {args.description or 'Auto-generated from CSV'}")
                logger.info(f"  Number of rules: {len(rules)}")
                logger.info(f"  Default access: BLOCK (deny all other traffic)")
            else:
                num_policies = (total_rules + MAX_L3ACL_RULES - 1) // MAX_L3ACL_RULES
                logger.info("DRY RUN: Would create the following policies:")
                for policy_num in range(num_policies):
                    start_idx = policy_num * MAX_L3ACL_RULES
                    end_idx = min(start_idx + MAX_L3ACL_RULES, total_rules)
                    policy_entries = csv_entries[start_idx:end_idx]
                    
                    policy_name = f"{args.policy_name}-{policy_num + 1}" if num_policies > 1 else args.policy_name
                    logger.info(f"  Policy {policy_num + 1}: {policy_name}")
                    logger.info(f"    Rules: {len(policy_entries)} (entries {start_idx + 1}-{end_idx})")
                    logger.info(f"    Default access: BLOCK")
            
            logger.info("  Sample rules:")
            sample_rules = create_l3_rules(csv_entries[:3])  # Show first 3 rules
            for i, rule in enumerate(sample_rules):
                logger.info(f"    Rule {i+1}: {rule['description']}")
            if total_rules > 3:
                logger.info(f"    ... and {total_rules - 3} more rules")
            logger.info("DRY RUN complete - no policies created")
            return
        
        # Initialize RUCKUS One client
        logger.info("Initializing RUCKUS One client...")
        
        # Load credentials from config file or environment variables
        config_path = Path(args.config)
        config_data = {}
        
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(str(config_path))
            if 'credentials' in config:
                config_data = {
                    'client_id': config['credentials'].get('client_id'),
                    'client_secret': config['credentials'].get('client_secret'),
                    'tenant_id': config['credentials'].get('tenant_id')
                }
        
        client_id = os.environ.get("R1_CLIENT_ID") or config_data.get('client_id')
        client_secret = os.environ.get("R1_CLIENT_SECRET") or config_data.get('client_secret')
        tenant_id = os.environ.get("R1_TENANT_ID") or config_data.get('tenant_id')
        
        if not all([client_id, client_secret, tenant_id]):
            logger.error("Missing authentication credentials. Set R1_CLIENT_ID, R1_CLIENT_SECRET, R1_TENANT_ID environment variables or create config file.")
            sys.exit(1)
            
        client = RuckusOneClient(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            region=args.region
        )
        
        # Create the L3 ACL policy(ies)
        responses = create_l3acl_policies(
            client=client,
            policy_name=args.policy_name,
            csv_entries=csv_entries,
            description=args.description,
            split_policies=args.split_policies
        )
        
        # Report results
        if len(responses) == 1:
            response = responses[0]
            if 'requestId' in response:
                logger.info(f"Policy creation initiated with requestId: {response['requestId']}")
                logger.info("You can monitor the request status using the RUCKUS One portal or API")
            logger.info("L3 ACL policy import completed successfully!")
        else:
            logger.info(f"Created {len(responses)} L3 ACL policies:")
            for i, response in enumerate(responses, 1):
                if 'requestId' in response:
                    logger.info(f"  Policy {i}: requestId {response['requestId']}")
            logger.info("You can monitor the request status using the RUCKUS One portal or API")
            logger.info("L3 ACL policies import completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Import failed: {e}")
        if args.verbose:
            logger.exception("Full error details:")
        sys.exit(1)


if __name__ == "__main__":
    main()