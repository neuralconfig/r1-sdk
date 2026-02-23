"""
Interactive CLI for the RUCKUS One SDK.

This module provides an interactive command-line interface for the RUCKUS One SDK,
similar to a network switch CLI with tab completion and "?" help functionality.
"""

import os
import sys
import cmd2
import configparser
import json
import logging
import shlex
from typing import Dict, Any, Optional, List, Tuple

from .. import __version__
from ..client import RuckusOneClient
from ..exceptions import APIError, AuthenticationError
from .main import load_config


class VenueMode(cmd2.CommandSet):
    """Command set for venue configuration mode."""
    
    def __init__(self, parent):
        """Initialize the command set."""
        super().__init__()
        self.parent = parent
        
    def do_list(self, args):
        """List all venues."""
        if not self.parent.require_auth():
            return
            
        try:
            venues = self.parent.client.venues.list(
                search_string=None,
                page_size=10,
                page=0
            )
            
            # Display venues in a table
            if 'data' in venues and venues['data']:
                self.parent.poutput("\nVenues:")
                self.parent.poutput(f"{'ID':<36} | {'Name':<30} | {'City':<20} | {'Country':<10}")
                self.parent.poutput("-" * 100)
                
                for venue in venues['data']:
                    venue_id = venue.get('id', 'N/A')
                    name = venue.get('name', 'N/A')
                    city = venue.get('city', 'N/A')
                    country = venue.get('country', 'N/A')
                    self.parent.poutput(f"{venue_id:<36} | {name:<30} | {city:<20} | {country:<10}")
                
                self.parent.poutput(f"\nShowing {len(venues['data'])} of {venues.get('totalItems', 'unknown')} venues")
            else:
                self.parent.poutput("No venues found.")
                
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")
            
    def do_show(self, args):
        """Show venue details.
        
        Usage: show <venue-id>
        """
        if not self.parent.require_auth():
            return
            
        # Get venue ID from arguments
        args = shlex.split(args)
        if not args:
            self.parent.perror("Venue ID is required")
            return
            
        venue_id = args[0]
        
        try:
            venue = self.parent.client.venues.get(venue_id)
            
            # Display venue details
            self.parent.poutput("\nVenue Details:")
            self.parent.poutput(f"ID: {venue.get('id', 'N/A')}")
            self.parent.poutput(f"Name: {venue.get('name', 'N/A')}")
            self.parent.poutput(f"Address: {venue.get('addressLine', 'N/A')}")
            self.parent.poutput(f"City: {venue.get('city', 'N/A')}")
            self.parent.poutput(f"State/Province: {venue.get('stateOrProvince', 'N/A')}")
            self.parent.poutput(f"Country: {venue.get('country', 'N/A')}")
            self.parent.poutput(f"Postal Code: {venue.get('postalCode', 'N/A')}")
            self.parent.poutput(f"Timezone: {venue.get('timezone', 'N/A')}")
            self.parent.poutput(f"Status: {venue.get('status', 'N/A')}")
            
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")


class APMode(cmd2.CommandSet):
    """Command set for AP configuration mode."""
    
    def __init__(self, parent):
        """Initialize the command set."""
        super().__init__()
        self.parent = parent
        
    def do_list(self, args):
        """List access points.
        
        Usage: list [venue-id]
        """
        if not self.parent.require_auth():
            return
            
        # Get venue ID from arguments if provided
        args = shlex.split(args)
        venue_id = args[0] if args else None
        
        try:
            filters = {}
            if venue_id:
                filters["venueId"] = venue_id
                
            aps = self.parent.client.aps.list(
                search_string=None,
                page_size=10,
                page=0,
                **filters
            )
            
            # Display APs in a table
            if 'data' in aps and aps['data']:
                self.parent.poutput("\nAccess Points:")
                self.parent.poutput(f"{'Serial':<15} | {'Name':<25} | {'Model':<12} | {'Status':<8} | {'Venue ID':<36}")
                self.parent.poutput("-" * 100)
                
                for ap in aps['data']:
                    serial = ap.get('serialNumber', 'N/A')
                    name = ap.get('name', 'N/A')
                    model = ap.get('model', 'N/A')
                    status = ap.get('status', 'N/A')
                    venue_id = ap.get('venueId', 'N/A')
                    self.parent.poutput(f"{serial:<15} | {name:<25} | {model:<12} | {status:<8} | {venue_id:<36}")
                
                self.parent.poutput(f"\nShowing {len(aps['data'])} of {aps.get('totalItems', 'unknown')} access points")
            else:
                self.parent.poutput("No access points found.")
                
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")
    
    def do_show(self, args):
        """Show access point details.
        
        Usage: show <venue-id> <ap-serial>
        """
        if not self.parent.require_auth():
            return
            
        # Get venue ID and AP serial from arguments
        args = shlex.split(args)
        if len(args) < 2:
            self.parent.perror("Venue ID and AP serial are required")
            return
            
        venue_id = args[0]
        ap_serial = args[1]
        
        try:
            ap = self.parent.client.aps.get(venue_id, ap_serial)
            
            # Display AP details
            self.parent.poutput("\nAccess Point Details:")
            self.parent.poutput(f"Serial: {ap.get('serialNumber', 'N/A')}")
            self.parent.poutput(f"Name: {ap.get('name', 'N/A')}")
            self.parent.poutput(f"Model: {ap.get('model', 'N/A')}")
            self.parent.poutput(f"Status: {ap.get('status', 'N/A')}")
            self.parent.poutput(f"MAC: {ap.get('macAddress', 'N/A')}")
            self.parent.poutput(f"IP: {ap.get('ipAddress', 'N/A')}")
            self.parent.poutput(f"Firmware: {ap.get('firmwareVersion', 'N/A')}")
            self.parent.poutput(f"Venue ID: {ap.get('venueId', 'N/A')}")
            
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")


class SwitchMode(cmd2.CommandSet):
    """Command set for Switch configuration mode."""
    
    def __init__(self, parent):
        """Initialize the command set."""
        super().__init__()
        self.parent = parent
        
    def do_list(self, args):
        """List switches."""
        if not self.parent.require_auth():
            return
            
        try:
            switches = self.parent.client.switches.list({
                "pageSize": 10,
                "page": 0,
                "sortOrder": "ASC"
            })
            
            # Display switches in a table
            if 'data' in switches and switches['data']:
                self.parent.poutput("\nSwitches:")
                self.parent.poutput(f"{'ID':<36} | {'Name':<25} | {'Model':<15} | {'Status':<8} | {'Venue ID':<36}")
                self.parent.poutput("-" * 100)
                
                for switch in switches['data']:
                    switch_id = switch.get('id', 'N/A')
                    name = switch.get('name', 'N/A')
                    model = switch.get('model', 'N/A')
                    status = switch.get('status', 'N/A')
                    venue_id = switch.get('venueId', 'N/A')
                    self.parent.poutput(f"{switch_id:<36} | {name:<25} | {model:<15} | {status:<8} | {venue_id:<36}")
                
                self.parent.poutput(f"\nShowing {len(switches['data'])} of {switches.get('totalItems', 'unknown')} switches")
            else:
                self.parent.poutput("No switches found.")
                
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")
    
    def do_show(self, args):
        """Show switch details.
        
        Usage: show <switch-id>
        """
        if not self.parent.require_auth():
            return
            
        # Get switch ID from arguments
        args = shlex.split(args)
        if not args:
            self.parent.perror("Switch ID is required")
            return
            
        switch_id = args[0]
        
        try:
            # Get switch details
            switch = self.parent.client.switches.get(switch_id)
            
            # Display switch details
            self.parent.poutput("\nSwitch Details:")
            self.parent.poutput(f"ID: {switch.get('id', 'N/A')}")
            self.parent.poutput(f"Name: {switch.get('name', 'N/A')}")
            self.parent.poutput(f"Model: {switch.get('model', 'N/A')}")
            self.parent.poutput(f"Serial: {switch.get('serialNumber', 'N/A')}")
            self.parent.poutput(f"Status: {switch.get('status', 'N/A')}")
            self.parent.poutput(f"IP: {switch.get('ip', 'N/A')}")
            self.parent.poutput(f"Firmware: {switch.get('firmwareVersion', 'N/A')}")
            self.parent.poutput(f"Venue ID: {switch.get('venueId', 'N/A')}")
            
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")


class WLANMode(cmd2.CommandSet):
    """Command set for WLAN configuration mode."""
    
    def __init__(self, parent):
        """Initialize the command set."""
        super().__init__()
        self.parent = parent
        
    def do_list(self, args):
        """List WLANs."""
        if not self.parent.require_auth():
            return
            
        try:
            wlans = self.parent.client.wlans.list(
                search_string=None,
                page_size=10,
                page=0
            )
            
            # Display WLANs in a table
            if 'data' in wlans and wlans['data']:
                self.parent.poutput("\nWLANs:")
                self.parent.poutput(f"{'ID':<36} | {'Name':<25} | {'SSID':<20} | {'Security':<15} | {'VLAN':<5}")
                self.parent.poutput("-" * 100)
                
                for wlan in wlans['data']:
                    wlan_id = wlan.get('id', 'N/A')
                    name = wlan.get('name', 'N/A')
                    ssid = wlan.get('ssid', 'N/A')
                    security = wlan.get('securityProtocol', 'N/A')
                    vlan = wlan.get('vlan', 'N/A')
                    self.parent.poutput(f"{wlan_id:<36} | {name:<25} | {ssid:<20} | {security:<15} | {vlan:<5}")
                
                self.parent.poutput(f"\nShowing {len(wlans['data'])} of {wlans.get('totalItems', 'unknown')} WLANs")
            else:
                self.parent.poutput("No WLANs found.")
                
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")
    
    def do_show(self, args):
        """Show WLAN details.
        
        Usage: show <wlan-id>
        """
        if not self.parent.require_auth():
            return
            
        # Get WLAN ID from arguments
        args = shlex.split(args)
        if not args:
            self.parent.perror("WLAN ID is required")
            return
            
        wlan_id = args[0]
        
        try:
            wlan = self.parent.client.wlans.get(wlan_id)
            
            # Display WLAN details
            self.parent.poutput("\nWLAN Details:")
            self.parent.poutput(f"ID: {wlan.get('id', 'N/A')}")
            self.parent.poutput(f"Name: {wlan.get('name', 'N/A')}")
            self.parent.poutput(f"SSID: {wlan.get('ssid', 'N/A')}")
            self.parent.poutput(f"Description: {wlan.get('description', 'N/A')}")
            self.parent.poutput(f"Security: {wlan.get('securityProtocol', 'N/A')}")
            self.parent.poutput(f"VLAN: {wlan.get('vlan', 'N/A')}")
            self.parent.poutput(f"Hidden: {wlan.get('hiddenSsid', False)}")
            
        except APIError as e:
            self.parent.perror(f"API error: {e}")
        except Exception as e:
            self.parent.perror(f"Error: {e}")


class RuckusOneCLI(cmd2.Cmd):
    """Interactive CLI for the RUCKUS One SDK."""
    
    def __init__(self):
        """Initialize the interactive CLI."""
        # Set up cmd2 options
        super().__init__(
            allow_cli_args=True,
            allow_redirection=True,
            persistent_history_file='~/.ruckus_one_history',
            command_sets=[],
            shortcuts={
                'exit': 'quit',
                'ls': 'list'
            },
            include_ipy=False
        )
        
        # Enable question mark for help
        self.register_postparsing_hook(self._handle_question_mark)
        
        # Configure cmd2 prompt and intro
        self.prompt = 'RUCKUS> '
        self.intro = f"""
RUCKUS One SDK Interactive CLI v{__version__}
Type '?' for help, TAB for command completion, 'exit' to quit.

Enter configuration mode with:
  venue        - Configure venues
  ap           - Configure access points
  switch       - Configure switches
  wlan         - Configure wireless networks
        """
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize client as None (will be set by authenticate command)
        self.client = None
        self.config_path = None
        self.auth_credentials = {
            'client_id': None,
            'client_secret': None,
            'tenant_id': None,
            'region': 'na'
        }
        
        # Create command sets for different configuration modes
        self.venue_mode = VenueMode(self)
        self.ap_mode = APMode(self)
        self.switch_mode = SwitchMode(self)
        self.wlan_mode = WLANMode(self)
        
    def _handle_question_mark(self, data: cmd2.plugin.PostparsingData) -> cmd2.plugin.PostparsingData:
        """Handle '?' at the end of a command for context-sensitive help."""
        if data.statement.raw.endswith('?'):
            # Get the command without the '?'
            command = data.statement.raw.rstrip('?').strip()
            
            if command:
                # Check if it's an existing command
                if hasattr(self, f'do_{command}') or command in self.shortcuts:
                    # Show help for that command
                    self.poutput(self.get_help_string(command))
                    data.stop = True
                else:
                    # Show available commands starting with this prefix
                    matches = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_') and cmd[3:].startswith(command)]
                    if matches:
                        self.poutput(f"Commands matching '{command}':")
                        for match in matches:
                            self.poutput(f"  {match}")
                    else:
                        self.poutput(f"No commands matching '{command}'")
                    data.stop = True
            else:
                # Show help menu
                self.do_help('')
                data.stop = True
                
        return data
        
    # --------- Authentication commands ---------
    
    auth_parser = cmd2.Cmd2ArgumentParser(description='Authenticate with RUCKUS One API')
    auth_group = auth_parser.add_argument_group('Authentication Options')
    auth_group.add_argument('-c', '--config', help='Path to config.ini file')
    auth_group.add_argument('--client-id', help='RUCKUS One OAuth2 client ID')
    auth_group.add_argument('--client-secret', help='RUCKUS One OAuth2 client secret')
    auth_group.add_argument('--tenant-id', help='RUCKUS One tenant ID')
    auth_group.add_argument('--region', help='RUCKUS One API region (na, eu, asia)')
    
    def do_authenticate(self, args):
        """Authenticate with the RUCKUS One API."""
        try:
            args = self.auth_parser.parse_args(args.arg_list)
            
            if args.config:
                self.config_path = args.config
                config = load_config(args.config)
                self.auth_credentials.update(config)
                self.poutput(f"Loaded credentials from {args.config}")
            
            # Override with args if provided
            if args.client_id:
                self.auth_credentials['client_id'] = args.client_id
            if args.client_secret:
                self.auth_credentials['client_secret'] = args.client_secret
            if args.tenant_id:
                self.auth_credentials['tenant_id'] = args.tenant_id
            if args.region:
                self.auth_credentials['region'] = args.region
            
            # Check if we need to prompt for missing credentials
            if not self.auth_credentials.get('client_id'):
                self.auth_credentials['client_id'] = self.read_token("Enter Client ID: ")
            if not self.auth_credentials.get('client_secret'):
                self.auth_credentials['client_secret'] = self.read_token("Enter Client Secret: ")
            if not self.auth_credentials.get('tenant_id'):
                self.auth_credentials['tenant_id'] = self.read_token("Enter Tenant ID: ")
            
            # Create client
            self.client = RuckusOneClient(
                client_id=self.auth_credentials['client_id'],
                client_secret=self.auth_credentials['client_secret'],
                tenant_id=self.auth_credentials['tenant_id'],
                region=self.auth_credentials['region']
            )
            
            self.poutput(f"Successfully authenticated with RUCKUS One API")
            self.poutput(f"Region: {self.auth_credentials['region']}")
            self.poutput(f"Tenant ID: {self.auth_credentials['tenant_id']}")
            
            # Update prompt to show authenticated status
            self.prompt = f"RUCKUS({self.auth_credentials['region']})> "
            
        except AuthenticationError as e:
            self.perror(f"Authentication failed: {e}")
        except Exception as e:
            self.perror(f"Error: {e}")
    
    def read_token(self, prompt_text):
        """Read a token with getpass to hide the input."""
        return self.read_secure(prompt_text)
    
    def do_status(self, _):
        """Show current authentication status."""
        if not self.client:
            self.poutput("Not authenticated. Use 'authenticate' to connect to RUCKUS One API.")
            return
        
        self.poutput("RUCKUS One API Status:")
        self.poutput(f"  Region: {self.auth_credentials['region']}")
        self.poutput(f"  Tenant ID: {self.auth_credentials['tenant_id']}")
        self.poutput(f"  Config file: {self.config_path or 'Not using config file'}")
        self.poutput("  Authenticated: Yes")
    
    # --------- Configuration mode commands ---------
    
    def do_venue(self, _):
        """Enter venue configuration mode."""
        if not self.require_auth():
            return
            
        # Check if we're already in a configuration mode
        if '/' in self.prompt:
            self.poutput("Exit current mode first with 'exit' before entering a new configuration mode.")
            return
            
        # Create a sub-shell for venue commands
        venue_shell = cmd2.CommandSet()
        venue_shell.do_list = self.venue_mode.do_list
        venue_shell.do_show = self.venue_mode.do_show
        
        self.poutput("Entering venue configuration mode. Type 'exit' to return to main menu.")
        self.poutput("Available commands: list, show")
        
        old_prompt = self.prompt
        self.prompt = self.prompt.replace('>', '/venue>')
        
        # Run command loop for venue mode
        self._run_cmd_mode(venue_shell)
        
        # Restore prompt
        self.prompt = old_prompt
    
    def do_ap(self, _):
        """Enter access point configuration mode."""
        if not self.require_auth():
            return
            
        # Check if we're already in a configuration mode
        if '/' in self.prompt:
            self.poutput("Exit current mode first with 'exit' before entering a new configuration mode.")
            return
            
        # Create a sub-shell for AP commands
        ap_shell = cmd2.CommandSet()
        ap_shell.do_list = self.ap_mode.do_list
        ap_shell.do_show = self.ap_mode.do_show
        
        self.poutput("Entering AP configuration mode. Type 'exit' to return to main menu.")
        self.poutput("Available commands: list, show")
        
        old_prompt = self.prompt
        self.prompt = self.prompt.replace('>', '/ap>')
        
        # Run command loop for AP mode
        self._run_cmd_mode(ap_shell)
        
        # Restore prompt
        self.prompt = old_prompt
    
    def do_switch(self, _):
        """Enter switch configuration mode."""
        if not self.require_auth():
            return
            
        # Check if we're already in a configuration mode
        if '/' in self.prompt:
            self.poutput("Exit current mode first with 'exit' before entering a new configuration mode.")
            return
            
        # Create a sub-shell for switch commands
        switch_shell = cmd2.CommandSet()
        switch_shell.do_list = self.switch_mode.do_list
        switch_shell.do_show = self.switch_mode.do_show
        
        self.poutput("Entering switch configuration mode. Type 'exit' to return to main menu.")
        self.poutput("Available commands: list, show")
        
        old_prompt = self.prompt
        self.prompt = self.prompt.replace('>', '/switch>')
        
        # Run command loop for switch mode
        self._run_cmd_mode(switch_shell)
        
        # Restore prompt
        self.prompt = old_prompt
    
    def do_wlan(self, _):
        """Enter WLAN configuration mode."""
        if not self.require_auth():
            return
            
        # Check if we're already in a configuration mode
        if '/' in self.prompt:
            self.poutput("Exit current mode first with 'exit' before entering a new configuration mode.")
            return
            
        # Create a sub-shell for WLAN commands
        wlan_shell = cmd2.CommandSet()
        wlan_shell.do_list = self.wlan_mode.do_list
        wlan_shell.do_show = self.wlan_mode.do_show
        
        self.poutput("Entering WLAN configuration mode. Type 'exit' to return to main menu.")
        self.poutput("Available commands: list, show")
        
        old_prompt = self.prompt
        self.prompt = self.prompt.replace('>', '/wlan>')
        
        # Run command loop for WLAN mode
        self._run_cmd_mode(wlan_shell)
        
        # Restore prompt
        self.prompt = old_prompt
    
    def _run_cmd_mode(self, cmd_set):
        """Run a nested command set as a sub-shell."""
        try:
            # Add command set to the context
            self.register_command_set(cmd_set)
            
            # Exit command for this mode
            def do_exit(_):
                """Exit the current configuration mode."""
                return True
                
            setattr(cmd_set, 'do_exit', do_exit)
            
            # Create a local command loop
            exit_code = False
            while not exit_code:
                try:
                    line = input(self.prompt)
                    if not line or line.strip() == "":
                        continue
                    if line.strip() == 'exit':
                        break
                        
                    # Handle command in the current mode
                    cmd_name = line.split()[0] if line.split() else ""
                    cmd_args = ' '.join(line.split()[1:]) if len(line.split()) > 1 else ""
                    
                    # Check if command exists in the command set
                    cmd_functions = [cmd[3:] for cmd in dir(cmd_set) if cmd.startswith('do_')]
                    if cmd_name in cmd_functions:
                        try:
                            func = getattr(cmd_set, f'do_{cmd_name}')
                            exit_code = func(cmd_args)
                        except Exception as e:
                            self.perror(f"Error executing {cmd_name}: {e}")
                    else:
                        # Block mode-switching commands
                        if cmd_name in ['venue', 'ap', 'switch', 'wlan']:
                            self.poutput(f"Exit current mode first with 'exit' before entering a new configuration mode.")
                        else:
                            # Use the main cmd2 processing for global commands
                            exit_code = self.onecmd_plus_hooks(line)
                except KeyboardInterrupt:
                    self.poutput("^C")
                except Exception as e:
                    self.perror(f"Error: {e}")
        finally:
            # Always remove command set to clean up, even if an exception occurs
            try:
                self.unregister_command_set(cmd_set)
            except Exception as e:
                # Just log the error but don't raise it to the user
                self.logger.debug(f"Error unregistering command set: {e}")
    
    # Helper methods
    
    def require_auth(self) -> bool:
        """Check if client is authenticated and print error if not."""
        if not self.client:
            self.perror("Not authenticated. Use 'authenticate' first.")
            return False
        return True


def main():
    """Launch the interactive CLI."""
    import sys
    import argparse
    
    # Parse command-line arguments for interactive mode
    parser = argparse.ArgumentParser(description='RUCKUS One Interactive CLI')
    parser.add_argument('--config', '-c', help='Path to config.ini file')
    
    args, _ = parser.parse_known_args(sys.argv[1:])
    
    cli = RuckusOneCLI()
    
    # If config file is specified, authenticate automatically
    if args.config:
        from cmd2.cmd2 import Statement
        cmd = f'authenticate -c {args.config}'
        cli.onecmd_plus_hooks(Statement(cmd))
        
    cli.cmdloop()


if __name__ == '__main__':
    main()