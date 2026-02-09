"""
CLI Templates module for the RUCKUS One API.

This module handles CLI template operations such as creating, retrieving,
updating, and deleting command-line interface templates for switches.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from ..exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class CLITemplates:
    """
    CLI Templates API module.

    Handles operations related to CLI templates in the RUCKUS One API.
    """

    def __init__(self, client):
        """
        Initialize the CLI Templates module.

        Args:
            client: RuckusOneClient instance
        """
        self.client = client
        # Register this module with the client for easier access
        self.client.cli_templates = self

    def list(self) -> List[Dict[str, Any]]:
        """
        List all CLI templates.

        Returns:
            List of CLI template dictionaries
        """
        logger.debug("Listing CLI templates")
        try:
            result = self.client.get("/cliTemplates")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} CLI templates")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.exception(f"Error listing CLI templates: {str(e)}")
            raise

    def get(self, template_id: str) -> Dict[str, Any]:
        """
        Retrieve a CLI template by ID.

        Args:
            template_id: ID of the CLI template to retrieve

        Returns:
            Dict containing CLI template details

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Getting CLI template: {template_id}")
        try:
            result = self.client.get(f"/cliTemplates/{template_id}")
            logger.debug(f"Retrieved CLI template: {result.get('name')} (ID: {result.get('id')})")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def create(self, name: str, cli: str, variables: Optional[List[Dict[str, Any]]] = None,
              reload: bool = False, venue_switches: Optional[List[Dict[str, Any]]] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Create a new CLI template.

        Args:
            name: Name of the CLI template
            cli: CLI commands for the template
            variables: List of template variables
            reload: Whether to reload after applying template
            venue_switches: List of venue switches to associate
            **kwargs: Additional template properties

        Returns:
            Dict containing the created CLI template details
        """
        logger.debug(f"Creating CLI template: {name}")

        data = {
            "name": name,
            "cli": cli,
            "reload": reload
        }

        if variables:
            data["variables"] = variables
        if venue_switches:
            data["venueSwitches"] = venue_switches

        # Add any additional properties
        data.update(kwargs)

        try:
            result = self.client.post("/cliTemplates", data=data)
            logger.debug(f"CLI template creation successful: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error creating CLI template: {str(e)}")
            raise

    def update(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing CLI template.

        Args:
            template_id: ID of the CLI template to update
            **kwargs: CLI template properties to update

        Returns:
            Dict containing the updated CLI template details

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Updating CLI template: {template_id} with data: {kwargs}")
        try:
            result = self.client.put(f"/cliTemplates/{template_id}", data=kwargs)
            logger.debug(f"CLI template update successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def delete(self, template_id: str) -> None:
        """
        Delete a CLI template.

        Args:
            template_id: ID of the CLI template to delete

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Deleting CLI template: {template_id}")
        try:
            self.client.delete(f"/cliTemplates/{template_id}")
            logger.debug("CLI template deletion successful")
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def query(self, query_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query CLI templates with filtering and pagination.

        Args:
            query_data: Query parameters including filters, pagination, etc.
                Example: {
                    "filters": [
                        {
                            "type": "NAME",
                            "value": "template_name"
                        }
                    ],
                    "pageSize": 100,
                    "page": 0,
                    "sortOrder": "ASC"
                }

        Returns:
            Dict containing CLI templates and pagination information
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

        logger.debug(f"Querying CLI templates with data: {query_data}")
        try:
            result = self.client.post("/cliTemplates/query", data=query_data)
            logger.debug(f"CLI templates query result keys: {list(result.keys()) if result else 'No result'}")
            return result
        except Exception as e:
            logger.exception(f"Error querying CLI templates: {str(e)}")
            raise

    def get_examples(self) -> List[Dict[str, Any]]:
        """
        Get CLI template examples.

        Returns:
            List of CLI template example dictionaries
        """
        logger.debug("Getting CLI template examples")
        try:
            result = self.client.get("/cliTemplates/examples")
            logger.debug(f"Retrieved {len(result) if isinstance(result, list) else '?'} CLI template examples")
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.exception(f"Error getting CLI template examples: {str(e)}")
            raise

    def associate_with_venue(self, venue_id: str, template_id: str, **kwargs) -> Dict[str, Any]:
        """
        Associate a CLI template with a venue.

        Args:
            venue_id: ID of the venue
            template_id: ID of the CLI template
            **kwargs: Additional association parameters

        Returns:
            Dict containing the association result

        Raises:
            ResourceNotFoundError: If the venue or CLI template does not exist
        """
        logger.debug(f"Associating CLI template {template_id} with venue {venue_id}")
        try:
            result = self.client.put(f"/venues/{venue_id}/cliTemplates/{template_id}", data=kwargs)
            logger.debug(f"CLI template association successful: {result}")
            return result
        except ResourceNotFoundError:
            logger.error(f"Venue {venue_id} or CLI template {template_id} not found")
            raise ResourceNotFoundError(
                message=f"Venue {venue_id} or CLI template {template_id} not found"
            )

    def disassociate_from_venue(self, venue_id: str, template_id: str) -> None:
        """
        Disassociate a CLI template from a venue.

        Args:
            venue_id: ID of the venue
            template_id: ID of the CLI template

        Raises:
            ResourceNotFoundError: If the venue or CLI template does not exist
        """
        logger.debug(f"Disassociating CLI template {template_id} from venue {venue_id}")
        try:
            self.client.delete(f"/venues/{venue_id}/cliTemplates/{template_id}")
            logger.debug("CLI template disassociation successful")
        except ResourceNotFoundError:
            logger.error(f"Venue {venue_id} or CLI template {template_id} not found")
            raise ResourceNotFoundError(
                message=f"Venue {venue_id} or CLI template {template_id} not found"
            )

    def bulk_delete(self, template_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple CLI templates.

        Args:
            template_ids: List of CLI template IDs to delete

        Returns:
            Dict containing the bulk deletion result
        """
        logger.debug(f"Bulk deleting CLI templates: {template_ids}")
        try:
            result = self.client.request('DELETE', "/cliTemplates", json_data=template_ids)
            logger.debug(f"CLI templates bulk deletion successful: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error bulk deleting CLI templates: {str(e)}")
            raise

    # Variable Management Methods

    def get_variables(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Get variables for a CLI template.

        Args:
            template_id: ID of the CLI template

        Returns:
            List of variable dictionaries

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Getting variables for CLI template: {template_id}")
        try:
            template = self.get(template_id)
            variables = template.get('variables', [])
            logger.debug(f"Retrieved {len(variables)} variables for CLI template")
            return variables
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def add_variable(self, template_id: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a variable to a CLI template.

        Args:
            template_id: ID of the CLI template
            variable_data: Variable data containing name, type, and value
                Example: {
                    "name": "mgmt_ip",
                    "type": "ADDRESS",
                    "value": "192.168.1.1_192.168.1.100_255.255.255.0"
                }

        Returns:
            Dict containing the updated CLI template

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Adding variable to CLI template {template_id}: {variable_data}")
        try:
            # Get current template
            template = self.get(template_id)

            # Get current variables and add the new one
            variables = template.get('variables', [])

            # Check if variable with same name already exists
            for var in variables:
                if var.get('name') == variable_data.get('name'):
                    raise ValueError(f"Variable '{variable_data.get('name')}' already exists")

            variables.append(variable_data)

            # Update the template with new variables
            result = self.update(template_id, variables=variables)
            logger.debug(f"Variable added successfully to CLI template")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def update_variable(self, template_id: str, variable_name: str, variable_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a variable in a CLI template.

        Args:
            template_id: ID of the CLI template
            variable_name: Name of the variable to update
            variable_data: Updated variable data

        Returns:
            Dict containing the updated CLI template

        Raises:
            ResourceNotFoundError: If the CLI template or variable does not exist
        """
        logger.debug(f"Updating variable '{variable_name}' in CLI template {template_id}")
        try:
            # Get current template
            template = self.get(template_id)

            # Get current variables and update the specified one
            variables = template.get('variables', [])
            variable_found = False

            for i, var in enumerate(variables):
                if var.get('name') == variable_name:
                    variables[i] = variable_data
                    variable_found = True
                    break

            if not variable_found:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI template {template_id}"
                )

            # Update the template with modified variables
            result = self.update(template_id, variables=variables)
            logger.debug(f"Variable '{variable_name}' updated successfully")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise

    def delete_variable(self, template_id: str, variable_name: str) -> Dict[str, Any]:
        """
        Delete a variable from a CLI template.

        Args:
            template_id: ID of the CLI template
            variable_name: Name of the variable to delete

        Returns:
            Dict containing the updated CLI template

        Raises:
            ResourceNotFoundError: If the CLI template or variable does not exist
        """
        logger.debug(f"Deleting variable '{variable_name}' from CLI template {template_id}")
        try:
            # Get current template
            template = self.get(template_id)

            # Get current variables and remove the specified one
            variables = template.get('variables', [])
            initial_count = len(variables)
            variables = [var for var in variables if var.get('name') != variable_name]

            if len(variables) == initial_count:
                raise ResourceNotFoundError(
                    message=f"Variable '{variable_name}' not found in CLI template {template_id}"
                )

            # Update the template with remaining variables
            result = self.update(template_id, variables=variables)
            logger.debug(f"Variable '{variable_name}' deleted successfully")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise

    # Venue Switches Management Methods

    def get_venue_switches(self, template_id: str) -> List[Dict[str, Any]]:
        """
        Get venue switches mapping for a CLI template.

        Args:
            template_id: ID of the CLI template

        Returns:
            List of venue switches mappings

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Getting venue switches for CLI template: {template_id}")
        try:
            template = self.get(template_id)
            venue_switches = template.get('venueSwitches', [])
            logger.debug(f"Retrieved {len(venue_switches)} venue switches for CLI template")
            return venue_switches
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def add_venue_switches(self, template_id: str, venue_id: str, switch_ids: List[str]) -> Dict[str, Any]:
        """
        Add switches to a venue for a CLI template.

        Args:
            template_id: ID of the CLI template
            venue_id: ID of the venue
            switch_ids: List of switch IDs to add

        Returns:
            Dict containing the updated CLI template

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Adding switches to venue {venue_id} for CLI template {template_id}: {switch_ids}")
        try:
            # Get current template
            template = self.get(template_id)

            # Get current venue switches
            venue_switches = template.get('venueSwitches', [])

            # Find existing venue mapping or create new one
            venue_mapping = None
            for vs in venue_switches:
                if vs.get('venueId') == venue_id:
                    venue_mapping = vs
                    break

            if venue_mapping:
                # Add switches to existing venue mapping
                existing_switches = venue_mapping.get('switches', [])
                updated_switches = list(set(existing_switches + switch_ids))
                venue_mapping['switches'] = updated_switches
            else:
                # Create new venue mapping
                venue_mapping = {
                    'venueId': venue_id,
                    'switches': switch_ids
                }
                venue_switches.append(venue_mapping)

            # Update the template with new venue switches
            result = self.update(template_id, venueSwitches=venue_switches)
            logger.debug(f"Switches added successfully to venue for CLI template")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )

    def remove_venue_switches(self, template_id: str, venue_id: str, switch_ids: List[str]) -> Dict[str, Any]:
        """
        Remove switches from a venue for a CLI template.

        Args:
            template_id: ID of the CLI template
            venue_id: ID of the venue
            switch_ids: List of switch IDs to remove

        Returns:
            Dict containing the updated CLI template

        Raises:
            ResourceNotFoundError: If the CLI template does not exist
        """
        logger.debug(f"Removing switches from venue {venue_id} for CLI template {template_id}: {switch_ids}")
        try:
            # Get current template
            template = self.get(template_id)

            # Get current venue switches
            venue_switches = template.get('venueSwitches', [])

            # Find and update venue mapping
            for vs in venue_switches:
                if vs.get('venueId') == venue_id:
                    existing_switches = vs.get('switches', [])
                    updated_switches = [sw for sw in existing_switches if sw not in switch_ids]
                    vs['switches'] = updated_switches
                    break

            # Remove empty venue mappings
            venue_switches = [vs for vs in venue_switches if vs.get('switches')]

            # Update the template with modified venue switches
            result = self.update(template_id, venueSwitches=venue_switches)
            logger.debug(f"Switches removed successfully from venue for CLI template")
            return result
        except ResourceNotFoundError:
            logger.error(f"CLI template with ID {template_id} not found")
            raise ResourceNotFoundError(
                message=f"CLI template with ID {template_id} not found"
            )