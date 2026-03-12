# Identities

Access via `client.identities`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list(page, page_size, **kwargs)

List identities across all identity groups.

```python
result = client.identities.list()
result = client.identities.list(page=0, page_size=50)
```

**Returns:** `dict`

---

### list_all(group_id, **kwargs)

Fetch all identities in a specific group using auto-pagination.

```python
all_identities = client.identities.list_all("group-uuid")
```

**Returns:** `list[dict]`

---

### query(...)

Query identities with advanced filtering.

```python
result = client.identities.query(dpsk_pool_id="pool-uuid", page=0, page_size=50)
result = client.identities.query(filter_params={"status": "ACTIVE"})
```

**Parameters:** `dpsk_pool_id`, `ethernet_port`, `filter_params`, `page`, `page_size`, `sort`

**Returns:** `dict`

---

### get(group_id, identity_id)

Get an identity by ID within a group.

```python
identity = client.identities.get("group-uuid", "identity-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(group_id, name, ...)

Create a new identity.

```python
identity = client.identities.create(
    group_id="group-uuid",
    name="John Doe",
    email="john@example.com",
    vlan=100,
    devices=[{"macAddress": "AA-BB-CC-DD-EE-FF"}]
)
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `group_id` | str | Yes | Identity group ID |
| `name` | str | Yes | Identity name |
| `email` | str | No | Email address |
| `description` | str | No | Description |
| `expiration_date` | str | No | ISO format date |
| `vlan` | int | No | VLAN (1-4094) |
| `devices` | list | No | Devices to associate |

**Returns:** `dict`

---

### update(group_id, identity_id, **kwargs)

Update an identity (PATCH).

```python
client.identities.update("group-uuid", "identity-uuid", name="Jane Doe")
```

**Returns:** `dict`

---

### delete(group_id, identity_id)

Delete an identity.

```python
client.identities.delete("group-uuid", "identity-uuid")
```

---

### get_devices(group_id, identity_id)

Get devices associated with an identity.

```python
devices = client.identities.get_devices("group-uuid", "identity-uuid")
```

**Returns:** `list[dict]`

---

### add_device(group_id, identity_id, mac_address, ...)

Add a device to an identity.

```python
client.identities.add_device("group-uuid", "identity-uuid", "AA-BB-CC-DD-EE-FF", name="Laptop")
```

**Raises:** `ValidationError` if MAC format is invalid (expects `XX-XX-XX-XX-XX-XX`)

**Returns:** `dict`

---

### remove_device(group_id, identity_id, mac_address)

Remove a device from an identity.

```python
client.identities.remove_device("group-uuid", "identity-uuid", "AA-BB-CC-DD-EE-FF")
```

---

### export_csv(...)

Export identities to CSV.

```python
csv_bytes = client.identities.export_csv()
csv_bytes = client.identities.export_csv(dpsk_pool_id="pool-uuid")
```

**Returns:** `bytes`

---

### import_csv(group_id, csv_file)

Import identities from CSV into a group.

```python
with open("identities.csv", "rb") as f:
    result = client.identities.import_csv("group-uuid", f.read())
```

**Returns:** `dict`

---

### bulk_delete(group_id, identity_ids)

Bulk delete multiple identities from a group.

```python
client.identities.bulk_delete("group-uuid", ["identity-uuid-1", "identity-uuid-2"])
```

---

### update_ethernet_ports(group_id, identity_id, venue_id, ethernet_ports)

Update ethernet port assignments for an identity.

```python
client.identities.update_ethernet_ports(
    "group-uuid",
    "identity-uuid",
    "venue-uuid",
    [{"macAddress": "AA-BB-CC-DD-EE-FF", "portIndex": 1}]
)
```

**Returns:** `dict`

---

### delete_ethernet_port(group_id, identity_id, mac_address, port_index)

Delete an ethernet port assignment from an identity.

```python
client.identities.delete_ethernet_port("group-uuid", "identity-uuid", "AA-BB-CC-DD-EE-FF", 1)
```

---

### retry_vni_allocation(group_id, identity_id)

Retry VNI allocation for an identity that previously failed.

```python
client.identities.retry_vni_allocation("group-uuid", "identity-uuid")
```

**Returns:** `dict`
