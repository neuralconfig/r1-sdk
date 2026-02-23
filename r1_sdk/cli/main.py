"""
Main CLI entry point for the RUCKUS One SDK.
"""

import argparse
import json
import os
import sys
import logging
import configparser
from typing import Dict, Any, Optional

from .. import __version__
from ..client import RuckusOneClient
from ..exceptions import APIError, AuthenticationError


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config(config_path: str) -> Dict[str, str]:
    """
    Load configuration from a config.ini file.
    
    Args:
        config_path: Path to the config.ini file
        
    Returns:
        Dictionary with configuration values
    """
    config = configparser.ConfigParser()
    
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


def get_client(args: argparse.Namespace) -> RuckusOneClient:
    """
    Create a RUCKUS One client from command-line arguments, config file, or environment variables.
    
    Args:
        args: Command-line arguments
        
    Returns:
        RuckusOneClient instance
    
    Raises:
        AuthenticationError: If authentication fails
    """
    # Load config from file if specified
    config = {}
    config_file = None
    
    # Check args for config
    if hasattr(args, 'config') and args.config:
        config_file = args.config
        
    # Check environment variable for config
    if not config_file and 'RUCKUS_CONFIG_FILE' in os.environ:
        config_file = os.environ['RUCKUS_CONFIG_FILE']
        
    if config_file:
        logging.debug(f"Loading config from file: {config_file}")
        config = load_config(config_file)
        logging.debug(f"Config loaded: {config}")
    
    # Get credentials from arguments, config file, or environment variables (in that order)
    region = (getattr(args, 'region', None) or 
              config.get('region') or 
              os.environ.get('RUCKUS_API_REGION', 'na'))
    
    client_id = (getattr(args, 'client_id', None) or 
                config.get('client_id') or 
                os.environ.get('RUCKUS_API_CLIENT_ID'))
    
    client_secret = (getattr(args, 'client_secret', None) or 
                    config.get('client_secret') or 
                    os.environ.get('RUCKUS_API_CLIENT_SECRET'))
    
    tenant_id = (getattr(args, 'tenant_id', None) or 
                config.get('tenant_id') or 
                os.environ.get('RUCKUS_API_TENANT_ID'))
    
    logging.debug(f"Credentials: region={region}, client_id={client_id}, tenant_id={tenant_id}")
    
    if not client_id:
        raise AuthenticationError("Client ID is required (--client-id, config file, or RUCKUS_API_CLIENT_ID)")
    if not client_secret:
        raise AuthenticationError("Client Secret is required (--client-secret, config file, or RUCKUS_API_CLIENT_SECRET)")
    if not tenant_id:
        raise AuthenticationError("Tenant ID is required (--tenant-id, config file, or RUCKUS_API_TENANT_ID)")
    
    # Create and return client
    logging.debug("Creating RuckusOneClient...")
    client = RuckusOneClient(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        region=region
    )
    logging.debug("RuckusOneClient created successfully")
    return client


def handle_venue_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle venue-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.venue_command == 'list':
        # List venues
        return client.venues.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page
        )
    elif args.venue_command == 'get':
        # Get venue details
        if not args.id:
            raise ValueError("Venue ID is required for 'get' command")
        return client.venues.get(args.id)
    elif args.venue_command == 'create':
        # Create venue
        if not args.name:
            raise ValueError("Venue name is required for 'create' command")
        if not args.address:
            raise ValueError("Venue address is required for 'create' command")
        
        # Parse address as JSON
        try:
            address = json.loads(args.address)
        except json.JSONDecodeError:
            raise ValueError("Address must be valid JSON")
        
        return client.venues.create(
            name=args.name,
            address=address,
            description=args.description,
            timezone=args.timezone
        )
    elif args.venue_command == 'update':
        # Update venue
        if not args.id:
            raise ValueError("Venue ID is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.venues.update(args.id, **props)
    elif args.venue_command == 'delete':
        # Delete venue
        if not args.id:
            raise ValueError("Venue ID is required for 'delete' command")
        client.venues.delete(args.id)
        return {"message": f"Venue {args.id} deleted successfully"}


def handle_ap_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle AP-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.ap_command == 'list':
        # List APs
        filters = {}
        if args.venue_id:
            filters["venueId"] = args.venue_id
            
        return client.aps.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page,
            **filters
        )
    elif args.ap_command == 'get':
        # Get AP details
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'get' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'get' command")
        return client.aps.get(args.venue_id, args.serial)
    elif args.ap_command == 'update':
        # Update AP
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'update' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.aps.update(args.venue_id, args.serial, **props)
    elif args.ap_command == 'reboot':
        # Reboot AP
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'reboot' command")
        if not args.serial:
            raise ValueError("AP serial number is required for 'reboot' command")
        return client.aps.reboot(args.venue_id, args.serial)


def handle_wlan_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle WLAN-related commands.
    
    Args:
        args: Command-line arguments
        client: RuckusOneClient instance
        
    Returns:
        Command result
    """
    if args.wlan_command == 'list':
        # List WLANs
        return client.wlans.list(
            search_string=args.search,
            page_size=args.page_size,
            page=args.page
        )
    elif args.wlan_command == 'get':
        # Get WLAN details
        if not args.id:
            raise ValueError("WLAN ID is required for 'get' command")
        return client.wlans.get(args.id)
    elif args.wlan_command == 'create':
        # Create WLAN
        if not args.name:
            raise ValueError("WLAN name is required for 'create' command")
        if not args.ssid:
            raise ValueError("SSID is required for 'create' command")
        if not args.security_type:
            raise ValueError("Security type is required for 'create' command")
            
        return client.wlans.create(
            name=args.name,
            ssid=args.ssid,
            security_type=args.security_type,
            vlan_id=args.vlan_id,
            hidden=args.hidden,
            description=args.description
        )
    elif args.wlan_command == 'update':
        # Update WLAN
        if not args.id:
            raise ValueError("WLAN ID is required for 'update' command")
            
        # Parse properties as JSON
        props = {}
        if args.properties:
            try:
                props = json.loads(args.properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON")
                
        return client.wlans.update(args.id, **props)
    elif args.wlan_command == 'delete':
        # Delete WLAN
        if not args.id:
            raise ValueError("WLAN ID is required for 'delete' command")
        client.wlans.delete(args.id)
        return {"message": f"WLAN {args.id} deleted successfully"}
    elif args.wlan_command == 'deploy':
        # Deploy WLAN to venue
        if not args.id:
            raise ValueError("WLAN ID is required for 'deploy' command")
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'deploy' command")
            
        return client.wlans.deploy_to_venue(
            wlan_id=args.id,
            venue_id=args.venue_id,
            ap_group_id=args.ap_group_id
        )
    elif args.wlan_command == 'undeploy':
        # Undeploy WLAN from venue
        if not args.id:
            raise ValueError("WLAN ID is required for 'undeploy' command")
        if not args.venue_id:
            raise ValueError("Venue ID is required for 'undeploy' command")
            
        client.wlans.undeploy_from_venue(
            wlan_id=args.id,
            venue_id=args.venue_id,
            ap_group_id=args.ap_group_id
        )
        return {"message": f"WLAN {args.id} undeployed from venue {args.venue_id}"}


def handle_dpsk_commands(args: argparse.Namespace, client: RuckusOneClient) -> Any:
    """
    Handle DPSK commands.
    
    Args:
        args: Command line arguments
        client: RUCKUS One API client
    
    Returns:
        Command result
    """
    if args.dpsk_command == 'list':
        # List DPSK services
        filters = {}
        if args.search:
            filters['searchString'] = args.search
        if args.page_size:
            filters['pageSize'] = args.page_size
        if args.page is not None:
            filters['page'] = args.page
            
        return client.dpsk.list_services(filters=filters if filters else None)
    elif args.dpsk_command == 'get':
        # Get DPSK service details
        if not args.id:
            raise ValueError("DPSK service ID is required for 'get' command")
        return client.dpsk.get_service(args.id)
    elif args.dpsk_command == 'create':
        # Create DPSK service
        if not args.name:
            raise ValueError("DPSK service name is required for 'create' command")
            
        kwargs = {
            'passphraseFormat': args.passphrase_format,
            'passphraseLength': args.passphrase_length,
            'expirationType': args.expiration_type
        }
        
        if args.device_limit:
            kwargs['deviceCountLimit'] = args.device_limit
            
        return client.dpsk.create_service(args.name, **kwargs)
    elif args.dpsk_command == 'delete':
        # Delete DPSK service
        if not args.id:
            raise ValueError("DPSK service ID is required for 'delete' command")
        client.dpsk.delete_service(args.id)
        return {"message": f"DPSK service {args.id} deleted successfully"}
    elif args.dpsk_command == 'passphrase-list':
        # List passphrases
        if not args.service_id:
            raise ValueError("DPSK service ID is required for 'passphrase-list' command")
            
        filters = {}
        if args.page_size:
            filters['pageSize'] = args.page_size
        if args.page is not None:
            filters['page'] = args.page
            
        return client.dpsk.list_passphrases(args.service_id, 
                                          filters=filters if filters else None)
    elif args.dpsk_command == 'passphrase-create':
        # Create passphrases
        if not args.service_id:
            raise ValueError("DPSK service ID is required for 'passphrase-create' command")
        if not args.username:
            raise ValueError("Username is required for 'passphrase-create' command")
            
        passphrases = []
        for i in range(args.count):
            passphrase_data = {
                'userName': f"{args.username}" if args.count == 1 else f"{args.username}_{i+1}"
            }
            if args.passphrase:
                passphrase_data['passphrase'] = args.passphrase
            if args.email:
                passphrase_data['email'] = args.email
                
            passphrases.append(passphrase_data)
            
        return client.dpsk.create_passphrases(args.service_id, passphrases)
    elif args.dpsk_command == 'export':
        # Export passphrases to CSV
        if not args.service_id:
            raise ValueError("DPSK service ID is required for 'export' command")
            
        csv_data = client.dpsk.export_passphrases_csv(args.service_id)
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(csv_data)
            return {"message": f"Passphrases exported to {args.output_file}"}
        else:
            # Return CSV data to be printed
            return {"csv": csv_data}


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='RUCKUS One CLI')
    
    # Global arguments
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', '-c', help='Path to config.ini file')
    parser.add_argument('--region', help='RUCKUS One API region (na, eu, asia)')
    parser.add_argument('--client-id', help='RUCKUS One OAuth2 client ID')
    parser.add_argument('--client-secret', help='RUCKUS One OAuth2 client secret')
    parser.add_argument('--tenant-id', help='RUCKUS One tenant ID')
    parser.add_argument('--output', '-o', choices=['json', 'table'], default='json',
                       help='Output format (default: json)')
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest='command', help='Command group')
    
    # Venue commands
    venue_parser = subparsers.add_parser('venue', help='Venue commands')
    venue_subparsers = venue_parser.add_subparsers(dest='venue_command', help='Venue command')
    
    # Venue list command
    venue_list_parser = venue_subparsers.add_parser('list', help='List venues')
    venue_list_parser.add_argument('--search', help='Search string')
    venue_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    venue_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # Venue get command
    venue_get_parser = venue_subparsers.add_parser('get', help='Get venue details')
    venue_get_parser.add_argument('--id', required=True, help='Venue ID')
    
    # Venue create command
    venue_create_parser = venue_subparsers.add_parser('create', help='Create a new venue')
    venue_create_parser.add_argument('--name', required=True, help='Venue name')
    venue_create_parser.add_argument('--address', required=True, 
                                   help='Venue address as JSON')
    venue_create_parser.add_argument('--description', help='Venue description')
    venue_create_parser.add_argument('--timezone', help='Venue timezone')
    
    # Venue update command
    venue_update_parser = venue_subparsers.add_parser('update', help='Update a venue')
    venue_update_parser.add_argument('--id', required=True, help='Venue ID')
    venue_update_parser.add_argument('--properties', required=True, 
                                   help='Properties to update as JSON')
    
    # Venue delete command
    venue_delete_parser = venue_subparsers.add_parser('delete', help='Delete a venue')
    venue_delete_parser.add_argument('--id', required=True, help='Venue ID')
    
    # AP commands
    ap_parser = subparsers.add_parser('ap', help='AP commands')
    ap_subparsers = ap_parser.add_subparsers(dest='ap_command', help='AP command')
    
    # AP list command
    ap_list_parser = ap_subparsers.add_parser('list', help='List APs')
    ap_list_parser.add_argument('--venue-id', help='Venue ID')
    ap_list_parser.add_argument('--search', help='Search string')
    ap_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    ap_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # AP get command
    ap_get_parser = ap_subparsers.add_parser('get', help='Get AP details')
    ap_get_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_get_parser.add_argument('--serial', required=True, help='AP serial number')
    
    # AP update command
    ap_update_parser = ap_subparsers.add_parser('update', help='Update an AP')
    ap_update_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_update_parser.add_argument('--serial', required=True, help='AP serial number')
    ap_update_parser.add_argument('--properties', required=True, 
                                help='Properties to update as JSON')
    
    # AP reboot command
    ap_reboot_parser = ap_subparsers.add_parser('reboot', help='Reboot an AP')
    ap_reboot_parser.add_argument('--venue-id', required=True, help='Venue ID')
    ap_reboot_parser.add_argument('--serial', required=True, help='AP serial number')
    
    # WLAN commands
    wlan_parser = subparsers.add_parser('wlan', help='WLAN commands')
    wlan_subparsers = wlan_parser.add_subparsers(dest='wlan_command', help='WLAN command')
    
    # WLAN list command
    wlan_list_parser = wlan_subparsers.add_parser('list', help='List WLANs')
    wlan_list_parser.add_argument('--search', help='Search string')
    wlan_list_parser.add_argument('--page-size', type=int, default=10, help='Page size')
    wlan_list_parser.add_argument('--page', type=int, default=0, help='Page number')
    
    # WLAN get command
    wlan_get_parser = wlan_subparsers.add_parser('get', help='Get WLAN details')
    wlan_get_parser.add_argument('--id', required=True, help='WLAN ID')
    
    # WLAN create command
    wlan_create_parser = wlan_subparsers.add_parser('create', help='Create a new WLAN')
    wlan_create_parser.add_argument('--name', required=True, help='WLAN name')
    wlan_create_parser.add_argument('--ssid', required=True, help='SSID')
    wlan_create_parser.add_argument('--security-type', required=True, 
                                  help='Security type')
    wlan_create_parser.add_argument('--vlan-id', type=int, help='VLAN ID')
    wlan_create_parser.add_argument('--hidden', action='store_true', 
                                  help='Hide SSID')
    wlan_create_parser.add_argument('--description', help='WLAN description')
    
    # WLAN update command
    wlan_update_parser = wlan_subparsers.add_parser('update', help='Update a WLAN')
    wlan_update_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_update_parser.add_argument('--properties', required=True, 
                                  help='Properties to update as JSON')
    
    # WLAN delete command
    wlan_delete_parser = wlan_subparsers.add_parser('delete', help='Delete a WLAN')
    wlan_delete_parser.add_argument('--id', required=True, help='WLAN ID')
    
    # WLAN deploy command
    wlan_deploy_parser = wlan_subparsers.add_parser('deploy', 
                                                 help='Deploy WLAN to venue')
    wlan_deploy_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_deploy_parser.add_argument('--venue-id', required=True, help='Venue ID')
    wlan_deploy_parser.add_argument('--ap-group-id', help='AP group ID')
    
    # WLAN undeploy command
    wlan_undeploy_parser = wlan_subparsers.add_parser('undeploy', 
                                                   help='Undeploy WLAN from venue')
    wlan_undeploy_parser.add_argument('--id', required=True, help='WLAN ID')
    wlan_undeploy_parser.add_argument('--venue-id', required=True, help='Venue ID')
    wlan_undeploy_parser.add_argument('--ap-group-id', help='AP group ID')
    
    # DPSK commands
    dpsk_parser = subparsers.add_parser('dpsk', help='DPSK commands')
    dpsk_subparsers = dpsk_parser.add_subparsers(dest='dpsk_command', help='DPSK command')
    
    # DPSK list command
    dpsk_list_parser = dpsk_subparsers.add_parser('list', help='List DPSK services')
    dpsk_list_parser.add_argument('--search', help='Search string')
    dpsk_list_parser.add_argument('--page-size', type=int, help='Page size')
    dpsk_list_parser.add_argument('--page', type=int, help='Page number')
    
    # DPSK get command
    dpsk_get_parser = dpsk_subparsers.add_parser('get', help='Get DPSK service details')
    dpsk_get_parser.add_argument('--id', required=True, help='DPSK service ID')
    
    # DPSK create command
    dpsk_create_parser = dpsk_subparsers.add_parser('create', help='Create a new DPSK service')
    dpsk_create_parser.add_argument('--name', required=True, help='DPSK service name')
    dpsk_create_parser.add_argument('--passphrase-format', choices=['MOST_SECURED', 'SECURED', 'SIMPLE'], 
                                   default='MOST_SECURED', help='Passphrase format')
    dpsk_create_parser.add_argument('--passphrase-length', type=int, default=18, 
                                   help='Passphrase length')
    dpsk_create_parser.add_argument('--device-limit', type=int, help='Device count limit')
    dpsk_create_parser.add_argument('--expiration-type', 
                                   choices=['NEVER', 'SPECIFIED_DATE', 'DURATION_FROM_FIRST_USE'],
                                   default='NEVER', help='Expiration type')
    
    # DPSK delete command
    dpsk_delete_parser = dpsk_subparsers.add_parser('delete', help='Delete a DPSK service')
    dpsk_delete_parser.add_argument('--id', required=True, help='DPSK service ID')
    
    # DPSK passphrase list command
    dpsk_pp_list_parser = dpsk_subparsers.add_parser('passphrase-list', 
                                                    help='List passphrases in a DPSK service')
    dpsk_pp_list_parser.add_argument('--service-id', required=True, help='DPSK service ID')
    dpsk_pp_list_parser.add_argument('--page-size', type=int, help='Page size')
    dpsk_pp_list_parser.add_argument('--page', type=int, help='Page number')
    
    # DPSK passphrase create command
    dpsk_pp_create_parser = dpsk_subparsers.add_parser('passphrase-create', 
                                                      help='Create passphrases')
    dpsk_pp_create_parser.add_argument('--service-id', required=True, help='DPSK service ID')
    dpsk_pp_create_parser.add_argument('--username', required=True, help='Username')
    dpsk_pp_create_parser.add_argument('--passphrase', help='Specific passphrase (optional)')
    dpsk_pp_create_parser.add_argument('--email', help='Email address')
    dpsk_pp_create_parser.add_argument('--count', type=int, default=1, 
                                     help='Number of passphrases to create')
    
    # DPSK export command
    dpsk_export_parser = dpsk_subparsers.add_parser('export', 
                                                   help='Export passphrases to CSV')
    dpsk_export_parser.add_argument('--service-id', required=True, help='DPSK service ID')
    dpsk_export_parser.add_argument('--output-file', help='Output CSV file (default: stdout)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # If no command specified, print help and exit
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    try:
        # Create client
        try:
            client = get_client(args)
        except Exception as e:
            logging.error(f"Error creating client: {e}")
            sys.exit(1)
        
        # Handle commands
        result = None
        if args.command == 'venue' and hasattr(args, 'venue_command') and args.venue_command:
            result = handle_venue_commands(args, client)
        elif args.command == 'ap' and hasattr(args, 'ap_command') and args.ap_command:
            result = handle_ap_commands(args, client)
        elif args.command == 'wlan' and hasattr(args, 'wlan_command') and args.wlan_command:
            result = handle_wlan_commands(args, client)
        elif args.command == 'dpsk' and hasattr(args, 'dpsk_command') and args.dpsk_command:
            result = handle_dpsk_commands(args, client)
        else:
            # Subcommand missing
            if args.command == 'venue':
                venue_parser.print_help()
            elif args.command == 'ap':
                ap_parser.print_help()
            elif args.command == 'wlan':
                wlan_parser.print_help()
            elif args.command == 'dpsk':
                dpsk_parser.print_help()
            sys.exit(1)
            
        # Output result
        if result:
            # Handle special case for CSV export
            if isinstance(result, dict) and 'csv' in result:
                print(result['csv'])
            elif args.output == 'json':
                print(json.dumps(result, indent=2))
            elif args.output == 'table':
                # Simple table output (just for example)
                if isinstance(result, dict) and 'data' in result and isinstance(result['data'], list):
                    # Print data items as table
                    data = result['data']
                    if data:
                        # Get keys from first item
                        keys = data[0].keys()
                        # Print header
                        print(' | '.join(keys))
                        print('-' * 80)
                        # Print rows
                        for item in data:
                            print(' | '.join(str(item.get(k, '')) for k in keys))
                else:
                    # Just print as JSON for non-tabular data
                    print(json.dumps(result, indent=2))
                    
    except APIError as e:
        logging.error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()