# RUCKUS ONE API Documentation

## Overview

The RUCKUS ONE API provides comprehensive network management capabilities for enterprise Wi-Fi and switching infrastructure. This RESTful API enables programmatic control of venues, access points, switches, WLANs, VLANs, and other network resources.

**Table of Contents:**
- [Overview](#overview)
- [Authentication](#authentication)
- [API Categories](#api-categories)
- [Core Network Management APIs](#core-network-management-apis)
- [Detailed API Reference](#detailed-api-reference)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [SDK Integration](#sdk-integration)

**Key Features:**
- Complete venue hierarchy management
- Wi-Fi network and WLAN configuration
- Switch port and VLAN management  
- Identity and access management
- Certificate and security services
- MSP (Managed Service Provider) support
- Real-time monitoring and events

## Base URLs and Regions

The RUCKUS ONE API is available in multiple regions:

- **North America:** `https://api.ruckus.cloud`
- **Europe:** `https://api.eu.ruckus.cloud` 
- **Asia:** `https://api.asia.ruckus.cloud`

### License and Terms of Service
Usage of this API is subject to RUCKUS licensing terms and service agreements.

### Upcoming Changes
API versioning and deprecation notices are communicated through official channels.

### Versioning
The API supports multiple versions with backward compatibility where possible.

## Authentication

### JWT Bearer Authentication

The API uses JSON Web Token (JWT) authentication with OAuth2 flow. All requests must include a valid JWT token in the Authorization header.

**Header Format:**
```
Authorization: Bearer <jwt_token>
```

### API Versioning

The API uses content negotiation for versioning. Include the appropriate version in the Accept header:

```
Accept: application/vnd.ruckus.v<version>+json
```

**Supported Versions:**
- v1, v2, v3, v4, v5, v6, v7, v8, v9, v10

### Authentication Flow

1. Obtain credentials (client_id, client_secret, tenant_id)
2. Request JWT token using OAuth2
3. Include token in all API requests
4. Refresh token as needed

## API Categories

### 1. Activities
View Activities API provides comprehensive activity monitoring and logging services.

**Key Operations:**
- `POST /activities` - Get Activities
- `GET /activities/{id}` - Get Activity Details  
- `POST /activities/devices` - Get Activity Devices
- `PUT /activities/notifications` - Update Activity Notification Options
- `DELETE /activities/schedule` - Delete Schedule

### 2. Authentication
API Authentication and JWT services for secure access management.

**Features:**
- JWT Bearer token authentication
- OAuth2 flow support
- Session management
- Multi-factor authentication
- API key management

### 3. Certificate Template
Comprehensive certificate management including Certificate Authority, Server/Client Certificates, and Device Certificates.

**Certificate Authority Operations:**
- `POST /certificate-authorities` - Create New Certificate Authority
- `GET /certificate-authorities/{id}` - Get Specific Certificate Authority
- `PATCH /certificate-authorities/{id}` - Update Certificate Authority
- `DELETE /certificate-authorities/{id}` - Delete Certificate Authority
- `POST /certificate-authorities/{id}/private-key/download` - Download Private Key
- `GET /certificate-authorities/{id}/certificate-chain` - Download Certificate Chain

**Certificate Template Operations:**
- `POST /certificate-templates` - Create Certificate Template
- `GET /certificate-templates/{id}` - Get Certificate Template
- `PATCH /certificate-templates/{id}` - Update Certificate Template
- `DELETE /certificate-templates/{id}` - Delete Certificate Template

### 4. Identity Management
Comprehensive identity and access management including DPSK services, Identity Groups, and External Identity.

**DPSK Service Management:**
- `GET /dpsk-pools` - Get DPSK Pools
- `POST /dpsk-pools` - Create New DPSK Pool
- `PATCH /dpsk-pools/{id}` - Update DPSK Pool
- `DELETE /dpsk-pools/{id}` - Delete DPSK Pool
- `POST /dpsk-pools/search` - Search DPSK Pools

**DPSK Passphrase Management:**
- `POST /dpsk-passphrases` - Create DPSK Passphrase
- `GET /dpsk-passphrases/{id}` - Get Specific DPSK Passphrase
- `PATCH /dpsk-passphrases/{id}` - Update DPSK Passphrase
- `DELETE /dpsk-passphrases/{id}` - Delete Passphrase
- `POST /dpsk-passphrases/import` - Import Passphrases from CSV
- `POST /dpsk-passphrases/export` - Export Passphrases to CSV

**Identity Group Operations:**
- `GET /identity-groups` - Get Identity Groups
- `POST /identity-groups` - Create Identity Group
- `PATCH /identity-groups/{id}` - Update Identity Group
- `DELETE /identity-groups/{id}` - Delete Identity Group
- `POST /identity-groups/export` - Export Identity Groups to CSV

### 5. MSP (Managed Service Provider)
Multi-tenant management services designed for managed service providers and enterprise customers.

**Key Features:**
- Multi-tenant organization management
- Partner and reseller support
- Delegation and access controls
- Billing and usage tracking
- White-label capabilities

### 6. Property Management
Property and location management services for enterprise and hospitality deployments.

**Features:**
- Property hierarchy management
- Room and space management
- Guest services integration
- Location-based services
- Asset tracking

### 7. Switch Services
Comprehensive enterprise switch management with advanced configuration capabilities.

**Switch Configuration Backup:**
- `POST /switches/backup` - Create Configuration Backup
- `GET /switches/backup/{id}` - Get Backup Details
- `POST /switches/restore` - Restore Configuration

**Switch Firmware Upgrade:**
- `POST /switches/firmware/upgrade` - Initiate Firmware Upgrade
- `GET /switches/firmware/status` - Get Upgrade Status
- `GET /switches/firmware/versions` - Get Available Firmware Versions

**Switch Ports Management:**
- `GET /switches/{switchId}/ports` - Get Switch Port Configuration
- `PATCH /switches/{switchId}/ports/{portId}` - Update Port Configuration
- `GET /switches/{switchId}/ports/statistics` - Get Port Statistics

**Switch VLAN Management:**
- `GET /switches/{switchId}/vlans` - Get Switch VLAN Configuration
- `POST /switches/{switchId}/vlans` - Create VLAN on Switch
- `PUT /switches/{switchId}/vlans/{vlanId}` - Update VLAN Configuration
- `DELETE /switches/{switchId}/vlans/{vlanId}` - Delete VLAN

**Switch Access Control List:**
- `GET /switches/{switchId}/acls` - Get Access Control Lists
- `POST /switches/{switchId}/acls` - Create ACL Rule
- `PUT /switches/{switchId}/acls/{aclId}` - Update ACL Rule
- `DELETE /switches/{switchId}/acls/{aclId}` - Delete ACL Rule

**Switch Static Routes:**
- `GET /switches/{switchId}/static-routes` - Get Static Routes
- `POST /switches/{switchId}/static-routes` - Create Static Route
- `PUT /switches/{switchId}/static-routes/{routeId}` - Update Static Route
- `DELETE /switches/{switchId}/static-routes/{routeId}` - Delete Static Route

### 8. Venues
Comprehensive venue hierarchy and location management system.

**Venue Management:**
- `GET /venues` - Access Venues
- `POST /venues` - Request/Create Venue
- `GET /venues/{venueId}` - Access Venue by ID
- `PUT /venues/{venueId}` - Replace/Update Venue
- `DELETE /venues/{venueId}` - Revoke Venue by ID
- `DELETE /venues` - Revoke Multiple Venues by IDs

**Floor Plan Management:**
- `GET /venues/{venueId}/floor-plans` - Access Floor Plans
- `POST /venues/{venueId}/floor-plans` - Request Floor Plan
- `GET /venues/{venueId}/floor-plans/{planId}` - Access Specific Floor Plan
- `PUT /venues/{venueId}/floor-plans/{planId}` - Replace Floor Plan
- `DELETE /venues/{venueId}/floor-plans/{planId}` - Revoke Floor Plan
- `POST /venues/{venueId}/floor-plans/upload-url` - Access Image Upload URL
- `GET /venues/{venueId}/floor-plans/download-url` - Access Image Download URL

### 9. VLAN Management
Comprehensive VLAN and IP address pool management.

**VLAN Pool Operations:**
- `GET /vlan-pools` - Get VLAN Pools
- `POST /vlan-pools` - Create VLAN Pool
- `GET /vlan-pools/{poolId}` - Get Specific VLAN Pool
- `PUT /vlan-pools/{poolId}` - Update VLAN Pool
- `DELETE /vlan-pools/{poolId}` - Delete VLAN Pool

**VLAN Pool Profile Management:**
- `GET /vlan-pool-profiles` - Get VLAN Pool Profiles
- `POST /vlan-pool-profiles` - Create VLAN Pool Profile
- `GET /vlan-pool-profiles/{profileId}` - Get Specific Profile
- `PUT /vlan-pool-profiles/{profileId}` - Update Profile
- `DELETE /vlan-pool-profiles/{profileId}` - Delete Profile

### 10. Wi-Fi Services
Comprehensive wireless network management with advanced features.

**Wi-Fi Network Management:**
- `GET /wifi-networks` - Get Networks
- `POST /wifi-networks` - Create Network
- `GET /wifi-networks/{networkId}` - Get Network Details
- `PUT /wifi-networks/{networkId}` - Update Network
- `DELETE /wifi-networks/{networkId}` - Delete Network
- `PUT /wifi-networks/{networkId}/venues/{venueId}/activate` - Activate Wi-Fi Network On Venue
- `DELETE /wifi-networks/{networkId}/venues/{venueId}/deactivate` - Deactivate Wi-Fi Network On Venue
- `GET /wifi-networks/{networkId}/venues/{venueId}/settings` - Get Venue Wi-Fi Network Settings
- `PUT /wifi-networks/{networkId}/venues/{venueId}/settings` - Update Venue Wi-Fi Network Settings

**Wi-Fi Portal Service Profile:**
- `GET /wifi-portal-profiles` - Get Portal Service Profiles
- `POST /wifi-portal-profiles` - Create Portal Service Profile
- `GET /wifi-portal-profiles/{profileId}` - Get Specific Profile
- `PUT /wifi-portal-profiles/{profileId}` - Update Profile
- `DELETE /wifi-portal-profiles/{profileId}` - Delete Profile

**Wi-Fi Calling Service Profile:**
- `GET /wifi-calling-profiles` - Get Calling Service Profiles
- `POST /wifi-calling-profiles` - Create Calling Service Profile
- `GET /wifi-calling-profiles/{profileId}` - Get Specific Profile
- `PUT /wifi-calling-profiles/{profileId}` - Update Profile
- `DELETE /wifi-calling-profiles/{profileId}` - Delete Profile

**Wi-Fi Network Activation:**
- `POST /wifi-networks/activate` - Activate Wi-Fi Network
- `POST /wifi-networks/deactivate` - Deactivate Wi-Fi Network
- `GET /wifi-networks/activation-status` - Get Activation Status

## Detailed API Reference

### Access Point Management

**AP Group Operations:**
- `GET /ap-groups` - Get AP Groups
- `POST /ap-groups` - Create AP Group
- `GET /ap-groups/{groupId}` - Get AP Group Details
- `PUT /ap-groups/{groupId}` - Update AP Group
- `DELETE /ap-groups/{groupId}` - Delete AP Group
- `GET /venues/{venueId}/ap-groups` - Get AP Groups by Venue
- `PUT /ap-groups/{groupId}/wifi-networks/{networkId}/activate` - Activate AP Group On Wi-Fi Network
- `DELETE /ap-groups/{groupId}/wifi-networks/{networkId}/deactivate` - Deactivate AP Group On Wi-Fi Network
- `GET /ap-groups/{groupId}/wifi-networks/{networkId}/settings` - Get AP Group Settings On Wi-Fi Network
- `PUT /ap-groups/{groupId}/wifi-networks/{networkId}/settings` - Update AP Group Settings On Wi-Fi Network

**Client Management:**
- `PATCH /clients/control` - Clients Control
- `PATCH /clients/{clientId}` - Patch AP Client

**AP SNMP Agent Profile:**
- `GET /ap-snmp-profiles` - Get AP SNMP Agent Profiles
- `POST /ap-snmp-profiles` - Create AP SNMP Agent Profile
- `GET /ap-snmp-profiles/{profileId}` - Get AP SNMP Profile
- `PUT /ap-snmp-profiles/{profileId}` - Update AP SNMP Agent Profile
- `DELETE /ap-snmp-profiles/{profileId}` - Delete AP SNMP Agent Profile
- `POST /ap-snmp-profiles/{profileId}/usage` - Get AP SNMP Agent Profile Usage

### Application Policy Management

**Application Policy Operations:**
- `GET /application-policies` - Get Application Policies
- `POST /application-policies` - Add Application Policy
- `GET /application-policies/{policyId}` - Get Application Policy
- `PUT /application-policies/{policyId}` - Update Application Policy
- `DELETE /application-policies/{policyId}` - Delete Application Policy
- `PUT /application-policies/{policyId}/access-control-profiles/{profileId}/activate` - Activate Application Policy On Access Control Profile
- `DELETE /application-policies/{policyId}/access-control-profiles/{profileId}/deactivate` - Deactivate Application Policy On Access Control Profile
- `PUT /application-policies/{policyId}/wifi-networks/{networkId}/activate` - Activate Application Policy On Wi-Fi Network
- `DELETE /application-policies/{policyId}/wifi-networks/{networkId}/deactivate` - Deactivate Application Policy On Wi-Fi Network

### DHCP Configuration Service Profile

**DHCP Profile Management:**
- `GET /dhcp-profiles` - Get DHCP Configuration Service Profiles
- `POST /dhcp-profiles` - Create DHCP Configuration Service Profile
- `GET /dhcp-profiles/{profileId}` - Get DHCP Configuration Service Profile
- `PUT /dhcp-profiles/{profileId}` - Update DHCP Configuration Service Profile
- `DELETE /dhcp-profiles/{profileId}` - Delete DHCP Configuration Service Profile
- `GET /aps/{apId}/dhcp-leases` - Get AP DHCP Client Leases
- `GET /aps/{apId}/dhcp-pools-usage` - Get DHCP Pools Usage in AP
- `PUT /venues/{venueId}/dhcp-profiles/{profileId}/activate` - Activate DHCP Configuration Service Profile On Venue
- `DELETE /venues/{venueId}/dhcp-profiles/{profileId}/deactivate` - Deactivate DHCP Configuration Service Profile On Venue
- `GET /venues/{venueId}/dhcp-profiles/{profileId}/settings` - Get DHCP Service Profile Settings of Venue
- `GET /venues/{venueId}/dhcp-leases` - Get Venue DHCP Leases
- `GET /venues/{venueId}/dhcp-pools-usage` - Get DHCP Pools Usage in Venue

### Access Control Profile Management

**Access Control Operations:**
- `GET /access-control-profiles` - Get Access Control Profiles
- `POST /access-control-profiles` - Create Access Control Profile
- `GET /access-control-profiles/{profileId}` - Get Access Control Profile
- `PUT /access-control-profiles/{profileId}` - Update Access Control Profile
- `DELETE /access-control-profiles/{profileId}` - Delete Access Control Profile

### Client Isolation Allowlist

**Isolation Allowlist Management:**
- `GET /client-isolation-allowlists` - Get Client Isolation Allowlists
- `POST /client-isolation-allowlists` - Create Client Isolation Allowlist
- `GET /client-isolation-allowlists/{id}` - Get Client Isolation Allowlist
- `PUT /client-isolation-allowlists/{id}` - Update Client Isolation Allowlist
- `DELETE /client-isolation-allowlists/{id}` - Delete Client Isolation Allowlist
- `POST /client-isolation-allowlists/venue-usage` - Get Venue Usage

### Hotspot 2.0 Management

**Hotspot 2.0 Operator:**
- `POST /hotspot-operators` - Create Hotspot 2.0 Operator
- `GET /hotspot-operators/{id}` - Get Hotspot 2.0 Operator
- `PUT /hotspot-operators/{id}` - Update Hotspot 2.0 Operator
- `DELETE /hotspot-operators/{id}` - Delete Hotspot 2.0 Operator
- `PUT /hotspot-operators/{id}/wifi-networks/{networkId}/activate` - Activate Hotspot 2.0 Operator On Wi-Fi Network
- `DELETE /hotspot-operators/{id}/wifi-networks/{networkId}/deactivate` - Deactivate Hotspot 2.0 Operator On Wi-Fi Network

### Rogue AP Detection

**Rogue AP Detection Policy:**
- `GET /rogue-ap-policies` - Get Rogue AP Detection Policies
- `POST /rogue-ap-policies` - Create Rogue AP Detection Policy
- `GET /rogue-ap-policies/{policyId}` - Get Rogue AP Detection Policy
- `PUT /rogue-ap-policies/{policyId}` - Update Rogue AP Detection Policy
- `DELETE /rogue-ap-policies/{policyId}` - Delete Rogue AP Detection Policy

## API Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "total": 100,
    "page": 1,
    "perPage": 20
  }
}
```

### Error Response  
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request parameters are invalid",
    "details": []
  }
}
```

### Quality of Service (QoS) Features

**QoS Map Set Operations:**
- `GET /wifi-networks/qos/default-rules` - Get Default Rules for QoS Map Set
- `GET /wifi-networks/qos/default-options` - Get Default Options for QoS Map Set

### External Service Integrations

**External WISPr Providers:**
- `GET /external-wispr-providers` - Get External WISPr Providers

**Hotspot 2.0 Integration:**
- `GET /hotspot/identity-providers` - Get Predefined Hotspot 2.0 Identity Providers
- `GET /hotspot/operators` - Get Predefined Hotspot 2.0 Operators

### Wi-Fi Recovery Network

**Recovery Network Management:**
- `GET /wifi-recovery/passphrase-settings` - Get Wi-Fi Recovery Network Passphrase Settings
- `PUT /wifi-recovery/passphrase-settings` - Update Wi-Fi Recovery Network Passphrase Settings

### Certificate Validation

**X509 Certificate Operations:**
- `POST /certificates/x509/validate` - Validate X509 Certificates

## Common Parameters

### Pagination
- `page` - Page number (default: 1)
- `perPage` - Items per page (default: 20, max: 100)
- `sortBy` - Sort field
- `sortOrder` - Sort direction (asc/desc)

### Filtering
- `filter` - Generic filter parameter
- `search` - Text search across relevant fields
- `status` - Filter by status (active/inactive/etc)

### Resource Selection
- `fields` - Specify fields to return
- `expand` - Include related resources
- `include` - Include additional data

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Rate Limit:** 1000 requests per hour per API key
- **Burst Limit:** 100 requests per minute
- **Headers:** Rate limit information included in response headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Codes

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error

### API Error Codes
- `INVALID_REQUEST` - Request validation failed
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMITED` - Rate limit exceeded
- `INTERNAL_ERROR` - Server error

## SDK and Integration

### Python SDK
The RUCKUS ONE Python SDK provides a convenient interface for API integration:

```python
from ruckus_one import RuckusOneClient

client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    tenant_id="your-tenant-id",
    region="na"  # or "eu", "asia"
)

# Venue Management
venues = client.venues.list()
venue = client.venues.get(venue_id="venue-123")
new_venue = client.venues.create({
    "name": "New Office Location",
    "address": "123 Main St",
    "city": "San Francisco",
    "country": "US"
})

# Wi-Fi Network Management
networks = client.wifi_networks.list()
network = client.wifi_networks.create({
    "name": "Corporate-WiFi",
    "ssid": "CorpNet",
    "security": {
        "type": "wpa2_enterprise",
        "encryption": "aes"
    }
})

# Switch Management
switches = client.switches.list()
switch_ports = client.switches.get_ports(switch_id="switch-456")

# VLAN Management
vlans = client.vlans.list()
vlan = client.vlans.create({
    "name": "Guest_VLAN",
    "vlan_id": 100,
    "ip_pool": "192.168.100.0/24"
})
```

### CLI Tool
Interactive and command-line interfaces available:

```bash
# Command-line mode
ruckus-cli venue list --config config.ini
ruckus-cli wifi-network list --venue-id <venue_id>
ruckus-cli switch list --config config.ini
ruckus-cli vlan list --config config.ini

# Interactive mode  
ruckus-cli --interactive --config config.ini
```

### Authentication Examples

#### Environment Variables
```bash
export R1_CLIENT_ID="your-client-id"
export R1_CLIENT_SECRET="your-client-secret"
export R1_TENANT_ID="your-tenant-id"
export R1_REGION="na"  # or "eu", "asia"
```

#### Configuration File
```ini
[auth]
client_id = your-client-id
client_secret = your-client-secret
tenant_id = your-tenant-id
region = na
```

#### Direct API Calls
```python
import requests

# Get JWT Token
auth_url = "https://api.ruckus.cloud/oauth/token"
auth_data = {
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "tenant_id": "your-tenant-id",
    "grant_type": "client_credentials"
}

response = requests.post(auth_url, json=auth_data)
token = response.json()["access_token"]

# Use Token in API Calls
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.ruckus.v1+json",
    "Content-Type": "application/json"
}

# Get Venues
venues_response = requests.get("https://api.ruckus.cloud/venues", headers=headers)
venues = venues_response.json()
```

## Additional API Categories

### 11. RUCKUS Edge
Edge networking services for SD-WAN and network edge management.

**Edge Device Management:**
- `POST /edge/devices` - Add Device
- `GET /edge/devices/{deviceId}` - Get Device
- `PATCH /edge/devices/{deviceId}` - Update Device
- `DELETE /edge/devices/{deviceId}` - Delete Device

**Edge Static Route Configuration:**
- `GET /edge/static-routes` - Get Static Route Configuration
- `PATCH /edge/static-routes` - Update Static Route Configuration

**Edge DHCP Services:**
- `POST /edge/dhcp` - Create DHCP
- `GET /edge/dhcp/{id}` - Get DHCP
- `PUT /edge/dhcp/{id}` - Update DHCP
- `DELETE /edge/dhcp/{id}` - Delete DHCP
- `PUT /edge/dhcp/{id}/activate` - Activate DHCP
- `DELETE /edge/dhcp/{id}/deactivate` - Deactivate DHCP

### 12. Workflow Device Enrollments
Device enrollment and registration workflows.

**Admin Enrollment Registration:**
- `POST /enrollments/registrations/query` - Query Enrollment Registrations
- `GET /enrollments/registrations/{id}` - Get Enrollment Registration Details

**Admin Enrollment API:**
- `POST /enrollments/query` - Query Enrollments
- `GET /enrollments/{id}` - Get Enrollments for Specific Identifier

### 13. Entitlements
License and entitlement management services.

**Entitlement Management:**
- `GET /entitlements` - Get Entitlements
- `PATCH /entitlements` - Update Entitlements
- `POST /entitlements/banners` - Get Entitlement Banners
- `POST /entitlements/compliance` - Get Compliance
- `GET /entitlements/summaries` - Get Entitlement Summaries

**Assignment Management:**
- `POST /entitlements/assignments/self` - Create Self Assignment
- `DELETE /entitlements/assignments/self` - Delete Self Assignment
- `PATCH /entitlements/assignments/self` - Update Self Assignment

### 14. Events and Alarms
Comprehensive event monitoring and alarm management.

**Alarm Management:**
- `POST /alarms` - Get Alarms
- `POST /alarms/venue-ap-network-data` - Get Alarms with Venue/AP/Network Data
- `PATCH /alarms/{id}/clear` - Clear Alarm

**Event Management:**
- `POST /events` - Get Events
- `POST /events/export` - Export Events Within Date Range
- `POST /events/details` - Get Event Details with Venue/AP/Network Data
- `POST /events/historical-clients` - Get Historical Clients
- `GET /events/admin-logins` - Get Admin Members Last Logins

### 15. External Authentication Service
External authentication integration services.

**SAML Identity Provider:**
- `POST /saml-identity-providers` - Create SAML Identity Provider Profile
- `GET /saml-identity-providers/{id}` - Get SAML Identity Provider Profile
- `PATCH /saml-identity-providers/{id}` - Update SAML Identity Provider Profile
- `PUT /saml-identity-providers/{id}` - Update Entire SAML Identity Provider Profile
- `DELETE /saml-identity-providers/{id}` - Delete SAML Identity Provider Profile
- `PUT /saml-identity-providers/{id}/encryption-certificate/activate` - Activate Encryption Certificate
- `DELETE /saml-identity-providers/{id}/encryption-certificate/deactivate` - Deactivate Encryption Certificate

### 16. Files
File upload and download services.

**File Operations:**
- `POST /files/upload-url` - Get Upload URL
- `GET /files/{id}/download-url` - Get Download URL
- `GET /files/{id}/download` - Get File Download URL

### 17. MAC Registration
MAC address registration and management services.

**Registration Pool Management:**
- `GET /mac-registration-pools` - Get Registration Pools
- `POST /mac-registration-pools` - Create Registration Pool
- `GET /mac-registration-pools/{poolId}` - Get Specific Registration Pool
- `PATCH /mac-registration-pools/{poolId}` - Update Registration Pool
- `DELETE /mac-registration-pools/{poolId}` - Delete Registration Pool
- `POST /mac-registration-pools/search` - Search Registration Pools

**MAC Registration Management:**
- `GET /mac-registration-pools/{poolId}/registrations` - Get MAC Registrations
- `POST /mac-registration-pools/{poolId}/registrations` - Create MAC Registration
- `GET /mac-registrations/{id}` - Get Specific MAC Registration
- `PATCH /mac-registrations/{id}` - Update MAC Registration
- `DELETE /mac-registrations/{id}` - Delete MAC Registration
- `POST /mac-registrations/import` - Import MAC Registrations
- `POST /mac-registrations/search` - Search MAC Registrations

### 18. Message Templates
Message template management for notifications and communications.

**Template Management:**
- `GET /message-templates` - Retrieve All Templates in Scope
- `GET /message-templates/{id}` - Retrieve Specific Template

**Template Scope Management:**
- `GET /message-template-scopes` - Retrieve All Template Scopes

### 19. View Model Resources
Resource viewing and reporting services.

**View MSP Operations:**
- `POST /view/msp/delegations` - Get Delegations
- `POST /view/msp/ec-inventory` - Get EC Inventory
- `POST /view/msp/ec-inventory/export` - Export EC Inventory
- `POST /view/msp/tech-partner-ecs` - Query MSP-ECs for Tech Partner

**View Switch Operations:**
- `POST /view/switches/aggregation` - Get Switches Aggregation Details
- `POST /view/switches/clients` - Get Switch Clients
- `POST /view/switches/ports` - Get Switch Ports
- `POST /view/switches/inventory/export` - Export Switch Inventory
- `POST /view/switches/venues` - Get Switches of Venue

**View Venue Operations:**
- `POST /view/venues` - Get Venues
- `GET /view/venues/{id}/ap-models` - Get Venue AP Models
- `POST /view/venues/{id}/rogue-aps` - Get Venue Rogue APs

## Best Practices

### 1. Authentication
- Store JWT tokens securely
- Implement token refresh logic
- Use appropriate scopes and permissions

### 2. Error Handling
- Check HTTP status codes
- Parse error responses for details
- Implement retry logic for transient errors

### 3. Rate Limiting
- Monitor rate limit headers
- Implement exponential backoff
- Cache responses when appropriate

### 4. Performance  
- Use pagination for large datasets
- Specify only required fields
- Implement connection pooling

### 5. Security
- Use HTTPS for all requests
- Validate SSL certificates
- Sanitize input parameters
- Follow principle of least privilege

## Support and Resources

### Documentation
- API Reference: [https://docs.ruckus.cloud/api/](https://docs.ruckus.cloud/api/)
- Developer Portal: [https://developers.ruckus.cloud/](https://developers.ruckus.cloud/)

### Community
- Developer Forums: [https://community.ruckus.cloud/](https://community.ruckus.cloud/)
- GitHub Repository: [https://github.com/ruckus-one/](https://github.com/ruckus-one/)

### Contact
- Technical Support: support@ruckus.cloud
- Developer Relations: developers@ruckus.cloud

## Utility Scripts and Tools

The SDK includes several utility scripts for network analysis and management:

### Inventory Report Generator
```bash
python inventory_report.py
```
Generates comprehensive inventory reports of all network resources including venues, access points, switches, WLANs, and VLANs.

### WLAN Analysis Tools
```bash
python wlan_venue_info.py    # Analyze WLAN-venue relationships
python wlan_info.py          # Detailed WLAN information and properties
```

### Network Configuration Validation
```bash
python validate_config.py    # Validate network configurations
python test_connectivity.py  # Test API connectivity and authentication
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify client credentials are correct
   - Check token expiration
   - Ensure proper region is specified

2. **Rate Limiting**
   - Implement exponential backoff
   - Monitor rate limit headers
   - Cache responses when possible

3. **Network Configuration Issues**
   - Validate VLAN assignments
   - Check venue-WLAN associations using `venueApGroups` field
   - Verify switch port configurations

### Debug Mode
```python
client = RuckusOneClient(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    tenant_id="your-tenant-id",
    debug=True  # Enable debug logging
)
```

## Advanced Features

### MSP and Multi-Tenant Support
- Organization hierarchy management
- Delegated administration
- Partner and reseller frameworks
- White-label customization

### Edge Computing Integration
- SD-WAN capabilities
- Edge device management
- Distributed network services
- Hybrid cloud connectivity

### Analytics and Reporting
- Real-time network monitoring
- Usage analytics and reporting
- Performance metrics
- Security event tracking

---

*This documentation was extracted and generated from the official RUCKUS ONE API specification. For the most current information and detailed parameter specifications, please refer to the official API documentation at [https://docs.ruckus.cloud/api/](https://docs.ruckus.cloud/api/).*