# Switch Profiles

Access via `client.switch_profiles`. See [common patterns](../common-patterns.md) for auth and pagination.

## Core Methods

### list()

List all switch profiles.

```python
profiles = client.switch_profiles.list()
```

**Returns:** `list[dict]`

---

### list_all(**kwargs)

Fetch all switch profiles using auto-pagination.

```python
all_profiles = client.switch_profiles.list_all()
```

**Returns:** `list[dict]`

---

### query(query_data)

Query switch profiles with filtering and pagination.

```python
result = client.switch_profiles.query()
result = client.switch_profiles.query({"filters": [{"type": "NAME", "value": "Core"}]})
```

**Returns:** `dict`

---

### get(profile_id)

Get a switch profile by ID.

```python
profile = client.switch_profiles.get("profile-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(name, ...)

Create a new switch profile.

```python
profile = client.switch_profiles.create(
    name="Access Profile",
    description="Standard access switch config",
    igmp_snooping="active",
    jumbo_mode=False
)
```

**Parameters:** `name`, `description`, `igmp_snooping`, `jumbo_mode`, `spanning_tree_priority`

**Returns:** `dict`

---

### update(profile_id, **kwargs)

Update a switch profile.

```python
client.switch_profiles.update("profile-uuid", name="Updated Profile")
```

**Returns:** `dict`

---

### delete(profile_id)

Delete a switch profile.

```python
client.switch_profiles.delete("profile-uuid")
```

---

### bulk_delete(profile_ids)

Delete multiple switch profiles.

```python
client.switch_profiles.bulk_delete(["id1", "id2"])
```

**Returns:** `dict`

---

## Venue Association Methods

### associate_with_venue(venue_id, profile_id, **kwargs)

Associate a switch profile with a venue.

```python
client.switch_profiles.associate_with_venue("venue-uuid", "profile-uuid")
```

**Returns:** `dict`

---

### disassociate_from_venue(venue_id, profile_id)

Remove a switch profile from a venue.

```python
client.switch_profiles.disassociate_from_venue("venue-uuid", "profile-uuid")
```

---

### get_venue_profiles(venue_id)

Get switch profiles associated with a venue.

```python
profiles = client.switch_profiles.get_venue_profiles("venue-uuid")
```

**Returns:** `list[dict]`

---

## ACL Methods

### get_acls(profile_id)

Get ACLs for a switch profile.

```python
acls = client.switch_profiles.get_acls("profile-uuid")
```

**Returns:** `list[dict]`

---

### add_acl(profile_id, acl_data)

Add an ACL to a switch profile.

```python
client.switch_profiles.add_acl("profile-uuid", {"name": "block-all", "rules": [...]})
```

**Returns:** `dict`

---

### update_acl(profile_id, acl_id, **kwargs)

Update an ACL.

```python
client.switch_profiles.update_acl("profile-uuid", "acl-uuid", name="updated-acl")
```

**Returns:** `dict`

---

### delete_acl(profile_id, acl_id)

Delete an ACL.

```python
client.switch_profiles.delete_acl("profile-uuid", "acl-uuid")
```

---

## VLAN Methods

### get_vlans(profile_id)

Get VLANs for a switch profile.

```python
vlans = client.switch_profiles.get_vlans("profile-uuid")
```

**Returns:** `list[dict]`

---

### add_vlan(profile_id, vlan_data)

Add a VLAN to a switch profile.

```python
client.switch_profiles.add_vlan("profile-uuid", {"id": 100, "name": "Data"})
```

**Returns:** `dict`

---

### update_vlan(profile_id, vlan_id, **kwargs)

Update a VLAN.

```python
client.switch_profiles.update_vlan("profile-uuid", "vlan-uuid", name="Voice")
```

**Returns:** `dict`

---

### delete_vlan(profile_id, vlan_id)

Delete a VLAN.

```python
client.switch_profiles.delete_vlan("profile-uuid", "vlan-uuid")
```

---

## Trusted Port Methods

### get_trusted_ports(profile_id)

Get trusted ports for a switch profile.

```python
ports = client.switch_profiles.get_trusted_ports("profile-uuid")
```

**Returns:** `list[dict]`

---

### add_trusted_port(profile_id, port_data)

Add a trusted port.

```python
client.switch_profiles.add_trusted_port("profile-uuid", {"portName": "1/1/1"})
```

**Returns:** `dict`

---

### update_trusted_port(profile_id, port_id, **kwargs)

Update a trusted port.

```python
client.switch_profiles.update_trusted_port("profile-uuid", "port-uuid", portName="1/1/2")
```

**Returns:** `dict`

---

### delete_trusted_port(profile_id, port_id)

Delete a trusted port.

```python
client.switch_profiles.delete_trusted_port("profile-uuid", "port-uuid")
```

---

## CLI Variable Methods

### get_cli_variables(profile_id)

Get CLI variables for a switch profile.

```python
variables = client.switch_profiles.get_cli_variables("profile-uuid")
```

**Returns:** `list[dict]`

---

### update_cli_variables(profile_id, variables)

Replace all CLI variables for a switch profile.

```python
client.switch_profiles.update_cli_variables("profile-uuid", [
    {"name": "mgmt_ip", "type": "ADDRESS", "value": "10.0.0.1_10.0.0.100_255.255.255.0"}
])
```

**Returns:** `dict`

---

### add_cli_variable(profile_id, variable_data)

Add a CLI variable.

```python
client.switch_profiles.add_cli_variable("profile-uuid", {
    "name": "hostname", "type": "TEXT", "value": "switch-01"
})
```

**Returns:** `dict`

**Raises:** `ValueError` if variable name already exists

---

### update_cli_variable(profile_id, variable_name, variable_data)

Update a CLI variable.

```python
client.switch_profiles.update_cli_variable("profile-uuid", "hostname", {
    "name": "hostname", "type": "TEXT", "value": "switch-02"
})
```

**Returns:** `dict`

---

### delete_cli_variable(profile_id, variable_name)

Delete a CLI variable.

```python
client.switch_profiles.delete_cli_variable("profile-uuid", "hostname")
```

**Returns:** `dict`

---

## Switch Mapping Methods

### get_cli_profile_switches(profile_id, venue_id)

Get switches mapped to CLI profiles in a venue.

```python
switches = client.switch_profiles.get_cli_profile_switches("profile-uuid", "venue-uuid")
```

**Returns:** `list[str]`

---

### map_switch_to_cli_profile(profile_id, venue_id, switch_id, ...)

Map a switch to a CLI profile in a venue.

```python
client.switch_profiles.map_switch_to_cli_profile(
    "profile-uuid", "venue-uuid", "switch-serial",
    variable_values={"hostname": "switch-01", "mgmt_ip": "10.0.0.1"}
)
```

**Returns:** `dict`

---

### unmap_switch_from_cli_profile(profile_id, venue_id, switch_id)

Remove a switch mapping from a CLI profile.

```python
client.switch_profiles.unmap_switch_from_cli_profile("profile-uuid", "venue-uuid", "switch-serial")
```

**Returns:** `dict`

---

### get_switch_variable_values(profile_id, switch_serial)

Get variable values assigned to a specific switch.

```python
values = client.switch_profiles.get_switch_variable_values("profile-uuid", "switch-serial")
```

**Returns:** `dict[str, str]`

---

### update_switch_variable_values(profile_id, switch_serial, values)

Update variable values for a specific switch.

```python
client.switch_profiles.update_switch_variable_values("profile-uuid", "switch-serial", {
    "hostname": "switch-02", "mgmt_ip": "10.0.0.2"
})
```

**Returns:** `dict`

---

### get_variable_switch_mappings(profile_id, variable_name)

Get all switch mappings for a specific variable.

```python
mappings = client.switch_profiles.get_variable_switch_mappings("profile-uuid", "hostname")
```

**Returns:** `list[dict[str, str]]`

---

### update_variable_switch_mapping(profile_id, variable_name, switch_serial, value)

Set a variable value for a specific switch.

```python
client.switch_profiles.update_variable_switch_mapping("profile-uuid", "hostname", "switch-serial", "switch-03")
```

**Returns:** `dict`

---

### delete_variable_switch_mapping(profile_id, variable_name, switch_serial)

Remove a variable value for a specific switch.

```python
client.switch_profiles.delete_variable_switch_mapping("profile-uuid", "hostname", "switch-serial")
```

**Returns:** `dict`

---

### get_all_switch_mappings(profile_id)

Get all switch-to-variable mappings for a profile.

```python
mappings = client.switch_profiles.get_all_switch_mappings("profile-uuid")
# Returns: {"switch-serial-1": {"hostname": "sw1", "mgmt_ip": "10.0.0.1"}, ...}
```

**Returns:** `dict[str, dict[str, str]]`

---

### get_mapped_switches(profile_id)

Get list of all switches mapped to this profile.

```python
switches = client.switch_profiles.get_mapped_switches("profile-uuid")
# Returns: ["switch-serial-1", "switch-serial-2", ...]
```

**Returns:** `list[str]`
