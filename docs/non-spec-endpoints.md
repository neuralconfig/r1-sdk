# Non-Spec Endpoints

SDK methods that call endpoints **not present** in the current OpenAPI spec (`openapi-specs/RUCKUS_One_Consolidated_API_03_11_2026.json`). These may work against the live API but aren't in the published specification.

| SDK Method | HTTP | Endpoint |
|------------|------|----------|
| `APs.get_statistics()` | GET | `/venues/{venueId}/aps/{serialNumber}/statistics` |
| `Switches.get_statistics()` | GET | `/venues/{venueId}/switches/{switchId}/statistics` |
| `Switches.reboot()` | POST | `/venues/{venueId}/switches/{switchId}/reboot` |
| `Switches.configure_port()` | PUT | `/venues/{venueId}/switches/{switchId}/ports/{portId}` |
| `APs.add_to_group()` | POST | `/venues/{venueId}/apGroups/{apGroupId}/members` |
| `CLITemplates.get_venue_switches()` | GET | `/venues/{venueId}/cliTemplates/{cliTemplateId}/switches` |

## Purpose

Track for future verification against the live API or updated spec. These endpoints may:
- Exist in the API but not in the published spec
- Have been added after the spec snapshot
- Be undocumented/internal endpoints

## Action Items

- Verify each endpoint against the live API
- If confirmed working, note for inclusion in future spec updates
- If not working, consider deprecating the SDK methods
