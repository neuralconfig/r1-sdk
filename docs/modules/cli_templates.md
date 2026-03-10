# CLI Templates

Access via `client.cli_templates`. See [common patterns](../common-patterns.md) for auth and pagination.

## Core Methods

### list()

List all CLI templates.

```python
templates = client.cli_templates.list()
```

**Returns:** `list[dict]`

---

### list_all(**kwargs)

Fetch all CLI templates using auto-pagination.

```python
all_templates = client.cli_templates.list_all()
```

**Returns:** `list[dict]`

---

### query(query_data)

Query CLI templates with filtering and pagination.

```python
result = client.cli_templates.query()
result = client.cli_templates.query({"filters": [{"type": "NAME", "value": "VLAN Config"}]})
```

**Returns:** `dict`

---

### get(template_id)

Get a CLI template by ID.

```python
template = client.cli_templates.get("template-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(name, cli, ...)

Create a new CLI template.

```python
template = client.cli_templates.create(
    name="VLAN Config",
    cli="vlan ${vlan_id}\n name ${vlan_name}\n exit",
    variables=[{"name": "vlan_id", "type": "TEXT", "value": "100"}],
    reload=False
)
```

**Parameters:** `name`, `cli`, `variables`, `reload`, `venue_switches`

**Returns:** `dict`

---

### update(template_id, **kwargs)

Update a CLI template.

```python
client.cli_templates.update("template-uuid", name="Updated Template", cli="new commands")
```

**Returns:** `dict`

---

### delete(template_id)

Delete a CLI template.

```python
client.cli_templates.delete("template-uuid")
```

---

### bulk_delete(template_ids)

Delete multiple CLI templates.

```python
client.cli_templates.bulk_delete(["id1", "id2", "id3"])
```

**Returns:** `dict`

---

### get_examples()

Get CLI template examples.

```python
examples = client.cli_templates.get_examples()
```

**Returns:** `list[dict]`

---

## Venue Association Methods

### associate_with_venue(venue_id, template_id, **kwargs)

Associate a CLI template with a venue.

```python
client.cli_templates.associate_with_venue("venue-uuid", "template-uuid")
```

**Returns:** `dict`

---

### disassociate_from_venue(venue_id, template_id)

Remove a CLI template association from a venue.

```python
client.cli_templates.disassociate_from_venue("venue-uuid", "template-uuid")
```

---

## Variable Management Methods

### get_variables(template_id)

Get variables for a CLI template.

```python
variables = client.cli_templates.get_variables("template-uuid")
```

**Returns:** `list[dict]`

---

### add_variable(template_id, variable_data)

Add a variable to a CLI template.

```python
client.cli_templates.add_variable("template-uuid", {
    "name": "mgmt_ip",
    "type": "ADDRESS",
    "value": "192.168.1.1_192.168.1.100_255.255.255.0"
})
```

**Returns:** `dict`

**Raises:** `ValueError` if variable name already exists

---

### update_variable(template_id, variable_name, variable_data)

Update a variable in a CLI template.

```python
client.cli_templates.update_variable("template-uuid", "mgmt_ip", {
    "name": "mgmt_ip",
    "type": "ADDRESS",
    "value": "10.0.0.1_10.0.0.100_255.255.255.0"
})
```

**Returns:** `dict`

---

### delete_variable(template_id, variable_name)

Delete a variable from a CLI template.

```python
client.cli_templates.delete_variable("template-uuid", "mgmt_ip")
```

**Returns:** `dict`

---

## Venue Switches Methods

### get_venue_switches(template_id)

Get venue switches mapping for a CLI template.

```python
mappings = client.cli_templates.get_venue_switches("template-uuid")
```

**Returns:** `list[dict]`

---

### add_venue_switches(template_id, venue_id, switch_ids)

Add switches to a venue mapping for a CLI template.

```python
client.cli_templates.add_venue_switches("template-uuid", "venue-uuid", ["switch-1", "switch-2"])
```

**Returns:** `dict`

---

### remove_venue_switches(template_id, venue_id, switch_ids)

Remove switches from a venue mapping for a CLI template.

```python
client.cli_templates.remove_venue_switches("template-uuid", "venue-uuid", ["switch-1"])
```

**Returns:** `dict`
