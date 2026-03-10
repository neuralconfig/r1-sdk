# Switches

Access via `client.switches`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list(query_data)

List switches with optional filtering.

```python
result = client.switches.list()
result = client.switches.list({"pageSize": 50, "filters": [{"type": "VENUE", "value": "venue-id"}]})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### list_all(query_data)

Fetch all switches using auto-pagination.

```python
all_switches = client.switches.list_all()
```

**Returns:** `list[dict]`

---

### get(venue_id, switch_id)

Get a switch by ID.

```python
switch = client.switches.get("venue-uuid", "switch-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### update(venue_id, switch_id, **kwargs)

Update a switch.

```python
client.switches.update("venue-uuid", "switch-uuid", name="Core Switch")
```

**Returns:** `dict`

---

### reboot(venue_id, switch_id)

Reboot a switch.

```python
client.switches.reboot("venue-uuid", "switch-uuid")
```

**Returns:** `dict`

---

### add_to_venue(venue_id, serial_number, name, ...)

Preprovision a switch to a venue. Supports both the documented API endpoint and the official Postman collection endpoint.

```python
# Full endpoint (default)
client.switches.add_to_venue("venue-uuid", "SWITCH-SERIAL", name="Access Switch")

# Simple endpoint (Postman style)
client.switches.add_to_venue("venue-uuid", "SWITCH-SERIAL", name="Access Switch", use_simple_endpoint=True)
```

**Key parameters:** `venue_id`, `serial_number`, `name`, `description`, `enable_stack`, `jumbo_mode`, `igmp_snooping`, `spanning_tree_priority`, `initial_vlan_id`, `trust_ports`, `stack_members`, `rear_module`, `specified_type`, `use_simple_endpoint`

**Returns:** `dict`

---

### remove_from_venue(venue_id, serial_number)

Remove a switch from a venue.

```python
client.switches.remove_from_venue("venue-uuid", "SWITCH-SERIAL")
```

---

### get_ports(query_data)

Query switch ports.

```python
ports = client.switches.get_ports({"filters": [{"type": "SWITCH", "value": "switch-id"}]})
```

**Returns:** `dict`

---

### configure_port(venue_id, switch_id, port_id, **kwargs)

Configure a switch port.

```python
client.switches.configure_port("venue-uuid", "switch-uuid", "port-uuid", poeEnabled=True)
```

**Returns:** `dict`

---

### get_vlans(venue_id, switch_id)

Get VLANs on a switch.

```python
vlans = client.switches.get_vlans("venue-uuid", "switch-uuid")
```

**Returns:** `dict`

---

### configure_vlan(venue_id, switch_id, vlan_id, **kwargs)

Configure an existing VLAN on a switch.

```python
client.switches.configure_vlan("venue-uuid", "switch-uuid", 100, name="Voice VLAN")
```

**Returns:** `dict`

---

### create_vlan(venue_id, switch_id, vlan_id, **kwargs)

Create a new VLAN on a switch.

```python
client.switches.create_vlan("venue-uuid", "switch-uuid", 200, name="Data VLAN")
```

**Returns:** `dict`

---

### delete_vlan(venue_id, switch_id, vlan_id)

Delete a VLAN from a switch.

```python
client.switches.delete_vlan("venue-uuid", "switch-uuid", 200)
```

---

### get_statistics(venue_id, switch_id)

Get switch statistics.

```python
stats = client.switches.get_statistics("venue-uuid", "switch-uuid")
```

**Returns:** `dict`
