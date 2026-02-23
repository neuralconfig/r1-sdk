"""
Switch Profiles module for the R1 API.

This module handles switch profile operations such as creating, retrieving,
updating, and deleting switch profiles, as well as managing their ACLs,
VLANs, and trusted ports.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class SwitchProfiles:
    """
    Switch Profiles API module.

    Handles operations related to switch profiles in the R1 API.
    """

    def __init__(self, client):
        """
        Initialize the Switch Profiles module.

        Args:
            client: R1Client instance
        """
        self.client = client

    def list(self) -> List[Dict[str, Any]]:
        """
        List all switch profiles.

        Returns:
            List of switch profile dictionaries
        """
        logger.debug("Listing switch profiles")
        try:
            result = self.client.get("/switchProfiles")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} switch profiles")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.exception(f"Error listing switch profiles: {str(e)}")
            raise

    def list_all(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch all switch profiles using auto-pagination. Returns flat list."""
        query_data = dict(kwargs)
        return self.client.paginate_query("/switchProfiles/query", query_data)

    def get(self, profile_id: str) -> Dict[str, Any]:
        """
        Retrieve a switch profile by ID.

        Args:
            profile_id: ID of the switch profile to retrieve

        Returns:
            Dict containing switch profile details

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Getting switch profile: {profile_id}")
        try:
            result = self.client.get(f"/switchProfiles/{profile_id}")
            logger.debug(f"Retrieved switch profile: {result.get('name')} (ID: {result.get('id')})")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def create(self, name: str, description: Optional[str] = None,
              profile_type: str = "Regular", apply_onboard_only: bool = False,
              **kwargs) -> Dict[str, Any]:
        """
        Create a new switch profile.

        Args:
            name: Name of the switch profile
            description: Description of the switch profile
            profile_type: Type of profile ("Regular" or "Template")
            apply_onboard_only: Whether to apply only during onboarding
            **kwargs: Additional profile properties

        Returns:
            Dict containing the created switch profile details
        """
        logger.debug(f"Creating switch profile: {name}")

        data = {
            "name": name,
            "profileType": profile_type,
            "applyOnboardOnly": apply_onboard_only
        }

        if description:
            data["description"] = description

        # Add any additional properties
        data.update(kwargs)

        try:
            result = self.client.post("/switchProfiles", data=data)
            logger.debug(f"Switch profile creation successful: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error creating switch profile: {str(e)}")
            raise

    def update(self, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing switch profile.

        Args:
            profile_id: ID of the switch profile to update
            **kwargs: Switch profile properties to update

        Returns:
            Dict containing the updated switch profile details

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Updating switch profile: {profile_id} with data: {kwargs}")
        try:
            result = self.client.put(f"/switchProfiles/{profile_id}", data=kwargs)
            logger.debug(f"Switch profile update successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def delete(self, profile_id: str) -> None:
        """
        Delete a switch profile.

        Args:
            profile_id: ID of the switch profile to delete

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Deleting switch profile: {profile_id}")
        try:
            self.client.delete(f"/switchProfiles/{profile_id}")
            logger.debug("Switch profile deletion successful")
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def query(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query switch profiles with filtering and pagination.

        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "NAME",
                            "value": "profile_name"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }

        Returns:
            Dict containing switch profiles and pagination information
        """
        # Prepare default query if none provided
        if query_data is None:
            query_data = {
                "pageSize": 100,
                "page": 1,
                "sortOrder": "ASC"
            }

        # Make sure sortOrder is uppercase
        if "sortOrder" in query_data:
            query_data["sortOrder"] = query_data["sortOrder"].upper()

        logger.debug(f"Querying switch profiles with data: {query_data}")
        try:
            result = self.client.post("/switchProfiles/query", data=query_data)
            logger.debug(f"Switch profiles query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying switch profiles: {str(e)}")
            raise

    # ACL Management Methods

    def get_acls(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get ACLs for a switch profile.

        Args:
            profile_id: ID of the switch profile

        Returns:
            List of ACL dictionaries

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Getting ACLs for switch profile: {profile_id}")
        try:
            result = self.client.get(f"/switchProfiles/{profile_id}/acls")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} ACLs")
            return result if isinstance(result, list) else []
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def add_acl(self, profile_id: str, acl_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an ACL to a switch profile.

        Args:
            profile_id: ID of the switch profile
            acl_data: ACL configuration data

        Returns:
            Dict containing the created ACL details

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Adding ACL to switch profile {profile_id}: {acl_data}")
        try:
            result = self.client.post(f"/switchProfiles/{profile_id}/acls", data=acl_data)
            logger.debug(f"ACL addition successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def update_acl(self, profile_id: str, acl_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an ACL in a switch profile.

        Args:
            profile_id: ID of the switch profile
            acl_id: ID of the ACL to update
            **kwargs: ACL properties to update

        Returns:
            Dict containing the updated ACL details

        Raises:
            ResourceNotFoundError: If the switch profile or ACL does not exist
        """
        logger.debug(f"Updating ACL {acl_id} in switch profile {profile_id}: {kwargs}")
        try:
            result = self.client.put(f"/switchProfiles/{profile_id}/acls/{acl_id}", data=kwargs)
            logger.debug(f"ACL update successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or ACL {acl_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or ACL {acl_id} not found"
            )

    def delete_acl(self, profile_id: str, acl_id: str) -> None:
        """
        Delete an ACL from a switch profile.

        Args:
            profile_id: ID of the switch profile
            acl_id: ID of the ACL to delete

        Raises:
            ResourceNotFoundError: If the switch profile or ACL does not exist
        """
        logger.debug(f"Deleting ACL {acl_id} from switch profile {profile_id}")
        try:
            self.client.delete(f"/switchProfiles/{profile_id}/acls/{acl_id}")
            logger.debug("ACL deletion successful")
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or ACL {acl_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or ACL {acl_id} not found"
            )

    # VLAN Management Methods

    def get_vlans(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get VLANs for a switch profile.

        Args:
            profile_id: ID of the switch profile

        Returns:
            List of VLAN dictionaries

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Getting VLANs for switch profile: {profile_id}")
        try:
            result = self.client.get(f"/switchProfiles/{profile_id}/vlans")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} VLANs")
            return result if isinstance(result, list) else []
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def add_vlan(self, profile_id: str, vlan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a VLAN to a switch profile.

        Args:
            profile_id: ID of the switch profile
            vlan_data: VLAN configuration data

        Returns:
            Dict containing the created VLAN details

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Adding VLAN to switch profile {profile_id}: {vlan_data}")
        try:
            result = self.client.post(f"/switchProfiles/{profile_id}/vlans", data=vlan_data)
            logger.debug(f"VLAN addition successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def update_vlan(self, profile_id: str, vlan_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a VLAN in a switch profile.

        Args:
            profile_id: ID of the switch profile
            vlan_id: ID of the VLAN to update
            **kwargs: VLAN properties to update

        Returns:
            Dict containing the updated VLAN details

        Raises:
            ResourceNotFoundError: If the switch profile or VLAN does not exist
        """
        logger.debug(f"Updating VLAN {vlan_id} in switch profile {profile_id}: {kwargs}")
        try:
            result = self.client.put(f"/switchProfiles/{profile_id}/vlans/{vlan_id}", data=kwargs)
            logger.debug(f"VLAN update successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or VLAN {vlan_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or VLAN {vlan_id} not found"
            )

    def delete_vlan(self, profile_id: str, vlan_id: str) -> None:
        """
        Delete a VLAN from a switch profile.

        Args:
            profile_id: ID of the switch profile
            vlan_id: ID of the VLAN to delete

        Raises:
            ResourceNotFoundError: If the switch profile or VLAN does not exist
        """
        logger.debug(f"Deleting VLAN {vlan_id} from switch profile {profile_id}")
        try:
            self.client.delete(f"/switchProfiles/{profile_id}/vlans/{vlan_id}")
            logger.debug("VLAN deletion successful")
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or VLAN {vlan_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or VLAN {vlan_id} not found"
            )

    # Trusted Ports Management Methods

    def get_trusted_ports(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get trusted ports for a switch profile.

        Args:
            profile_id: ID of the switch profile

        Returns:
            List of trusted port dictionaries

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Getting trusted ports for switch profile: {profile_id}")
        try:
            result = self.client.get(f"/switchProfiles/{profile_id}/trustedPorts")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} trusted ports")
            return result if isinstance(result, list) else []
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def add_trusted_port(self, profile_id: str, port_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a trusted port to a switch profile.

        Args:
            profile_id: ID of the switch profile
            port_data: Trusted port configuration data

        Returns:
            Dict containing the created trusted port details

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
        """
        logger.debug(f"Adding trusted port to switch profile {profile_id}: {port_data}")
        try:
            result = self.client.post(f"/switchProfiles/{profile_id}/trustedPorts", data=port_data)
            logger.debug(f"Trusted port addition successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def update_trusted_port(self, profile_id: str, port_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a trusted port in a switch profile.

        Args:
            profile_id: ID of the switch profile
            port_id: ID of the trusted port to update
            **kwargs: Trusted port properties to update

        Returns:
            Dict containing the updated trusted port details

        Raises:
            ResourceNotFoundError: If the switch profile or trusted port does not exist
        """
        logger.debug(f"Updating trusted port {port_id} in switch profile {profile_id}: {kwargs}")
        try:
            result = self.client.put(f"/switchProfiles/{profile_id}/trustedPorts/{port_id}", data=kwargs)
            logger.debug(f"Trusted port update successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or trusted port {port_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or trusted port {port_id} not found"
            )

    def delete_trusted_port(self, profile_id: str, port_id: str) -> None:
        """
        Delete a trusted port from a switch profile.

        Args:
            profile_id: ID of the switch profile
            port_id: ID of the trusted port to delete

        Raises:
            ResourceNotFoundError: If the switch profile or trusted port does not exist
        """
        logger.debug(f"Deleting trusted port {port_id} from switch profile {profile_id}")
        try:
            self.client.delete(f"/switchProfiles/{profile_id}/trustedPorts/{port_id}")
            logger.debug("Trusted port deletion successful")
        except ResourceNotFoundError:
            logger.error(f"Switch profile {profile_id} or trusted port {port_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile {profile_id} or trusted port {port_id} not found"
            )

    # Venue Association Methods

    def associate_with_venue(self, venue_id: str, profile_id: str, **kwargs) -> Dict[str, Any]:
        """
        Associate a switch profile with a venue.

        Args:
            venue_id: ID of the venue
            profile_id: ID of the switch profile
            **kwargs: Additional association parameters

        Returns:
            Dict containing the association result

        Raises:
            ResourceNotFoundError: If the venue or switch profile does not exist
        """
        logger.debug(f"Associating switch profile {profile_id} with venue {venue_id}")
        try:
            result = self.client.put(f"/venues/{venue_id}/switchProfiles/{profile_id}", data=kwargs)
            logger.debug(f"Switch profile association successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Venue {venue_id} or switch profile {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Venue {venue_id} or switch profile {profile_id} not found"
            )

    def disassociate_from_venue(self, venue_id: str, profile_id: str) -> None:
        """
        Disassociate a switch profile from a venue.

        Args:
            venue_id: ID of the venue
            profile_id: ID of the switch profile

        Raises:
            ResourceNotFoundError: If the venue or switch profile does not exist
        """
        logger.debug(f"Disassociating switch profile {profile_id} from venue {venue_id}")
        try:
            self.client.delete(f"/venues/{venue_id}/switchProfiles/{profile_id}")
            logger.debug("Switch profile disassociation successful")
        except ResourceNotFoundError:
            logger.error(f"Venue {venue_id} or switch profile {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Venue {venue_id} or switch profile {profile_id} not found"
            )

    def get_venue_profiles(self, venue_id: str) -> List[Dict[str, Any]]:
        """
        Get switch profiles associated with a venue.

        Args:
            venue_id: ID of the venue

        Returns:
            List of switch profile dictionaries

        Raises:
            ResourceNotFoundError: If the venue does not exist
        """
        logger.debug(f"Getting switch profiles for venue: {venue_id}")
        try:
            result = self.client.get(f"/venues/{venue_id}/switchProfiles")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} switch profiles for venue")
            return result if isinstance(result, list) else []
        except ResourceNotFoundError:
            logger.error(f"Venue with ID {venue_id} not found")
            raise ResourceNotFoundError(
                message=f"Venue with ID {venue_id} not found"
            )

    def bulk_delete(self, profile_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple switch profiles.

        Args:
            profile_ids: List of switch profile IDs to delete

        Returns:
            Dict containing the bulk deletion result
        """
        logger.debug(f"Bulk deleting switch profiles: {profile_ids}")
        try:
            result = self.client.request('DELETE', "/switchProfiles", json_data=profile_ids)
            logger.debug(f"Switch profiles bulk deletion successful: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error bulk deleting switch profiles: {str(e)}")
            raise

    # CLI Profile Variable Management Methods

    def get_cli_variables(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get variables from a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile

        Returns:
            List of variable dictionaries

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting CLI variables for switch profile: {profile_id}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            cli_template = profile.get('venueCliTemplate', {})
            variables = cli_template.get('variables', [])
            logger.debug(f"Retrieved {len(variables)} variables from CLI profile")
            return variables
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def update_cli_variables(self, profile_id: str, variables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update variables in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            variables: List of variable dictionaries

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Updating CLI variables for switch profile {profile_id}: {variables}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            # Get current CLI template and update variables
            cli_template = profile.get('venueCliTemplate', {})
            cli_template['variables'] = variables

            # Update the profile with full structure as required by API
            update_data = {
                'id': profile_id,
                'name': profile.get('name'),
                'profileType': 'CLI',
                'venueCliTemplate': cli_template,
                'venues': profile.get('venues', [])
            }
            result = self.client.put(f"/switchProfiles/{profile_id}", data=update_data)
            logger.debug(f"CLI variables updated successfully")
            return result
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def add_cli_variable(self, profile_id: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a variable to a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            variable_data: Variable data containing name, type, and value
                Example: {
                    "name": "vlan_id",
                    "type": "NUMBER",
                    "value": "100"
                }

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile or variable already exists
        """
        logger.debug(f"Adding CLI variable to switch profile {profile_id}: {variable_data}")
        try:
            # Get current variables
            variables = self.get_cli_variables(profile_id)

            # Check if variable with same name already exists
            for var in variables:
                if var.get('name') == variable_data.get('name'):
                    raise ValueError(f"Variable '{variable_data.get('name')}' already exists")

            # Add new variable
            variables.append(variable_data)

            # Update the profile with new variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"CLI variable added successfully")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def update_cli_variable(self, profile_id: str, variable_name: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a specific variable in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            variable_name: Name of the variable to update
            variable_data: Updated variable data

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile or variable does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Updating CLI variable '{variable_name}' in switch profile {profile_id}")
        try:
            # Get current variables
            variables = self.get_cli_variables(profile_id)

            # Find and update the specified variable
            variable_found = False
            for i, var in enumerate(variables):
                if var.get('name') == variable_name:
                    variables[i] = variable_data
                    variable_found = True
                    break

            if not variable_found:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI profile {profile_id}"
                )

            # Update the profile with modified variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"CLI variable '{variable_name}' updated successfully")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def delete_cli_variable(self, profile_id: str, variable_name: str) -> Dict[str, Any]:
        """
        Delete a variable from a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            variable_name: Name of the variable to delete

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile or variable does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Deleting CLI variable '{variable_name}' from switch profile {profile_id}")
        try:
            # Get current variables
            variables = self.get_cli_variables(profile_id)

            # Remove the specified variable
            initial_count = len(variables)
            variables = [var for var in variables if var.get('name') != variable_name]

            if len(variables) == initial_count:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI profile {profile_id}"
                )

            # Update the profile with remaining variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"CLI variable '{variable_name}' deleted successfully")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    # CLI Profile Switch Mapping Methods

    def get_cli_profile_switches(self, profile_id: str, venue_id: str) -> List[str]:
        """
        Get switches mapped to a CLI configuration profile for a specific venue.

        Args:
            profile_id: ID of the CLI switch profile
            venue_id: ID of the venue

        Returns:
            List of switch IDs mapped to the profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting switches for CLI profile {profile_id} in venue {venue_id}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            cli_template = profile.get('venueCliTemplate', {})
            venue_switches = cli_template.get('venueSwitches', [])

            # Find switches for the specified venue
            for vs in venue_switches:
                if vs.get('venueId') == venue_id:
                    switches = vs.get('switches', [])
                    logger.debug(f"Found {len(switches)} switches for venue {venue_id}")
                    return switches

            logger.debug(f"No switches found for venue {venue_id}")
            return []
        except ResourceNotFoundError:
            logger.error(f"Switch profile with ID {profile_id} not found")
            raise ResourceNotFoundError(
                message=f"Switch profile with ID {profile_id} not found"
            )

    def map_switch_to_cli_profile(self, profile_id: str, venue_id: str, switch_id: str,
                                  variable_values: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Map a switch to a CLI configuration profile with optional variable values.

        Args:
            profile_id: ID of the CLI switch profile
            venue_id: ID of the venue
            switch_id: ID of the switch to map
            variable_values: Optional dictionary of variable name -> value mappings

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Mapping switch {switch_id} to CLI profile {profile_id} in venue {venue_id}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            # Get current CLI template
            cli_template = profile.get('venueCliTemplate', {})
            venue_switches = cli_template.get('venueSwitches', [])

            # Find or create venue mapping
            venue_mapping = None
            for vs in venue_switches:
                if vs.get('venueId') == venue_id:
                    venue_mapping = vs
                    break

            if venue_mapping:
                # Add switch to existing venue mapping
                existing_switches = venue_mapping.get('switches', [])
                if switch_id not in existing_switches:
                    existing_switches.append(switch_id)
                    venue_mapping['switches'] = existing_switches
            else:
                # Create new venue mapping
                venue_mapping = {
                    'venueId': venue_id,
                    'switches': [switch_id]
                }
                venue_switches.append(venue_mapping)

            # Update variable values if provided
            if variable_values:
                # Store variable values in a switch-specific mapping
                # Note: The exact API structure for per-switch variable values may vary
                # This implementation assumes a switchVariables structure
                if 'switchVariables' not in venue_mapping:
                    venue_mapping['switchVariables'] = {}
                venue_mapping['switchVariables'][switch_id] = variable_values

            cli_template['venueSwitches'] = venue_switches

            # Update the profile (include name as it's mandatory)
            result = self.update(profile_id, name=profile.get('name'), venueCliTemplate=cli_template)
            logger.debug(f"Switch {switch_id} mapped successfully to CLI profile")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def unmap_switch_from_cli_profile(self, profile_id: str, venue_id: str, switch_id: str) -> Dict[str, Any]:
        """
        Remove a switch mapping from a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            venue_id: ID of the venue
            switch_id: ID of the switch to unmap

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Unmapping switch {switch_id} from CLI profile {profile_id} in venue {venue_id}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            # Get current CLI template
            cli_template = profile.get('venueCliTemplate', {})
            venue_switches = cli_template.get('venueSwitches', [])

            # Find and update venue mapping
            for vs in venue_switches:
                if vs.get('venueId') == venue_id:
                    existing_switches = vs.get('switches', [])
                    if switch_id in existing_switches:
                        existing_switches.remove(switch_id)
                        vs['switches'] = existing_switches

                        # Remove switch variable values if they exist
                        if 'switchVariables' in vs and switch_id in vs['switchVariables']:
                            del vs['switchVariables'][switch_id]
                    break

            # Remove empty venue mappings
            venue_switches = [vs for vs in venue_switches if vs.get('switches')]
            cli_template['venueSwitches'] = venue_switches

            # Update the profile (include name as it's mandatory)
            result = self.update(profile_id, name=profile.get('name'), venueCliTemplate=cli_template)
            logger.debug(f"Switch {switch_id} unmapped successfully from CLI profile")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def get_switch_variable_values(self, profile_id: str, switch_serial: str) -> Dict[str, str]:
        """
        Get variable values for a specific switch in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            switch_serial: Serial number of the switch

        Returns:
            Dict containing variable name -> value mappings

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting variable values for switch {switch_serial} in CLI profile {profile_id}")
        try:
            variables = self.get_cli_variables(profile_id)
            variable_values = {}

            # Extract switch-specific values from each variable
            for variable in variables:
                var_name = variable.get('name')
                switch_variables = variable.get('switchVariables', [])

                # Find this switch's value for this variable
                for mapping in switch_variables:
                    serial_numbers = mapping.get('serialNumbers', [])
                    if switch_serial in serial_numbers:
                        variable_values[var_name] = mapping.get('value')
                        break
                else:
                    # If no specific value found, use the default value
                    variable_values[var_name] = variable.get('value', '')

            logger.debug(f"Found {len(variable_values)} variable values for switch {switch_serial}")
            return variable_values
        except (ResourceNotFoundError, ValueError):
            raise

    def update_switch_variable_values(self, profile_id: str, switch_serial: str,
                                      variable_values: Dict[str, str]) -> Dict[str, Any]:
        """
        Update variable values for a specific switch in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            switch_serial: Serial number of the switch
            variable_values: Dict containing variable name -> value mappings

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Updating variable values for switch {switch_serial} in CLI profile {profile_id}: {variable_values}")
        try:
            profile = self.get(profile_id)

            if profile.get('profileType') != 'CLI':
                raise ValueError(f"Switch profile {profile_id} is not a CLI profile")

            # Get current variables
            variables = self.get_cli_variables(profile_id)

            # Update switch mappings in each variable
            for variable in variables:
                var_name = variable.get('name')
                if var_name in variable_values:
                    new_value = variable_values[var_name]

                    # Initialize switchVariables list if it doesn't exist
                    if 'switchVariables' not in variable:
                        variable['switchVariables'] = []

                    # Find existing mapping for this switch
                    switch_found = False
                    for mapping in variable['switchVariables']:
                        serial_numbers = mapping.get('serialNumbers', [])
                        if switch_serial in serial_numbers:
                            mapping['value'] = new_value
                            switch_found = True
                            break

                    # If switch not found, add new mapping
                    if not switch_found:
                        variable['switchVariables'].append({
                            'serialNumbers': [switch_serial],
                            'value': new_value
                        })

            # Update the profile with modified variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"Variable values updated successfully for switch {switch_serial}")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def get_variable_switch_mappings(self, profile_id: str, variable_name: str) -> List[Dict[str, str]]:
        """
        Get all switch mappings for a specific variable in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile
            variable_name: Name of the variable

        Returns:
            List of switch mappings containing serial and value

        Raises:
            ResourceNotFoundError: If the switch profile or variable does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting switch mappings for variable '{variable_name}' in CLI profile {profile_id}")
        try:
            variables = self.get_cli_variables(profile_id)

            # Find the specified variable
            for variable in variables:
                if variable.get('name') == variable_name:
                    switch_variables = variable.get('switchVariables', [])
                    # Convert to simpler format for easier consumption
                    switch_mappings = []
                    for mapping in switch_variables:
                        for serial in mapping.get('serialNumbers', []):
                            switch_mappings.append({
                                'serial': serial,
                                'value': mapping.get('value'),
                                'id': mapping.get('id')
                            })
                    logger.debug(f"Found {len(switch_mappings)} switch mappings for variable '{variable_name}'")
                    return switch_mappings

            raise ResourceNotFoundError(
                message=f"Variable '{variable_name}' not found in CLI profile {profile_id}"
            )
        except (ResourceNotFoundError, ValueError):
            raise

    def update_variable_switch_mapping(self, profile_id: str, variable_name: str,
                                     switch_serial: str, value: str) -> Dict[str, Any]:
        """
        Update or add a switch mapping for a specific variable.

        Args:
            profile_id: ID of the CLI switch profile
            variable_name: Name of the variable
            switch_serial: Serial number of the switch
            value: Value to assign to this switch for this variable

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile or variable does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Updating switch mapping for variable '{variable_name}' in CLI profile {profile_id}: {switch_serial} -> {value}")
        try:
            variables = self.get_cli_variables(profile_id)

            # Find and update the specified variable
            variable_found = False
            for variable in variables:
                if variable.get('name') == variable_name:
                    variable_found = True

                    # Initialize switchVariables list if it doesn't exist
                    if 'switchVariables' not in variable:
                        variable['switchVariables'] = []

                    # Find existing mapping for this switch
                    switch_found = False
                    for mapping in variable['switchVariables']:
                        serial_numbers = mapping.get('serialNumbers', [])
                        if switch_serial in serial_numbers:
                            mapping['value'] = value
                            switch_found = True
                            break

                    # If switch not found, add new mapping
                    if not switch_found:
                        variable['switchVariables'].append({
                            'serialNumbers': [switch_serial],
                            'value': value
                        })
                    break

            if not variable_found:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI profile {profile_id}"
                )

            # Update the profile with modified variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"Switch mapping updated successfully for variable '{variable_name}'")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def delete_variable_switch_mapping(self, profile_id: str, variable_name: str,
                                     switch_serial: str) -> Dict[str, Any]:
        """
        Remove a switch mapping from a specific variable.

        Args:
            profile_id: ID of the CLI switch profile
            variable_name: Name of the variable
            switch_serial: Serial number of the switch to remove

        Returns:
            Dict containing the updated switch profile

        Raises:
            ResourceNotFoundError: If the switch profile, variable, or switch mapping does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Deleting switch mapping for variable '{variable_name}' in CLI profile {profile_id}: {switch_serial}")
        try:
            variables = self.get_cli_variables(profile_id)

            # Find and update the specified variable
            variable_found = False
            switch_found = False
            for variable in variables:
                if variable.get('name') == variable_name:
                    variable_found = True

                    if 'switchVariables' in variable:
                        initial_count = len(variable['switchVariables'])
                        # Remove switch from existing mappings
                        for mapping in variable['switchVariables'][:]:
                            serial_numbers = mapping.get('serialNumbers', [])
                            if switch_serial in serial_numbers:
                                serial_numbers.remove(switch_serial)
                                switch_found = True
                                # If no more serials in this mapping, remove it entirely
                                if not serial_numbers:
                                    variable['switchVariables'].remove(mapping)
                    break

            if not variable_found:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI profile {profile_id}"
                )

            if not switch_found:
                raise ResourceNotFoundError(
                    message=f"Switch '{switch_serial}' mapping not found for variable '{variable_name}' in CLI profile {profile_id}"
                )

            # Update the profile with modified variables
            result = self.update_cli_variables(profile_id, variables)
            logger.debug(f"Switch mapping deleted successfully for variable '{variable_name}'")
            return result
        except (ResourceNotFoundError, ValueError):
            raise

    def get_all_switch_mappings(self, profile_id: str) -> Dict[str, Dict[str, str]]:
        """
        Get all switch-to-variable mappings for a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile

        Returns:
            Dict where keys are switch serials and values are dicts of variable_name -> value mappings

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting all switch mappings for CLI profile {profile_id}")
        try:
            variables = self.get_cli_variables(profile_id)
            switch_mappings = {}

            # Extract all switch mappings from all variables
            for variable in variables:
                var_name = variable.get('name')
                switch_variables = variable.get('switchVariables', [])

                for mapping in switch_variables:
                    serial_numbers = mapping.get('serialNumbers', [])
                    value = mapping.get('value')

                    for switch_serial in serial_numbers:
                        if switch_serial not in switch_mappings:
                            switch_mappings[switch_serial] = {}
                        switch_mappings[switch_serial][var_name] = value

            logger.debug(f"Found mappings for {len(switch_mappings)} switches")
            return switch_mappings
        except (ResourceNotFoundError, ValueError):
            raise

    def get_mapped_switches(self, profile_id: str) -> List[str]:
        """
        Get list of all switches that have variable mappings in a CLI configuration profile.

        Args:
            profile_id: ID of the CLI switch profile

        Returns:
            List of switch serial numbers

        Raises:
            ResourceNotFoundError: If the switch profile does not exist
            ValueError: If the profile is not a CLI profile
        """
        logger.debug(f"Getting mapped switches for CLI profile {profile_id}")
        try:
            all_mappings = self.get_all_switch_mappings(profile_id)
            switch_serials = list(all_mappings.keys())
            logger.debug(f"Found {len(switch_serials)} mapped switches")
            return switch_serials
        except (ResourceNotFoundError, ValueError):
            raise