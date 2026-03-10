# APs (Access Points)

Access via `client.aps`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list(query_data)

List APs with optional filtering.

```python
result = client.aps.list()
result = client.aps.list({"pageSize": 50, "page": 0, "filters": [{"type": "VENUE", "value": "venue-id"}]})
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `query_data` | dict \| None | None | Query with filters, pagination, sort |

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### list_all(query_data)

Fetch all APs using auto-pagination.

```python
all_aps = client.aps.list_all()
```

**Returns:** `list[dict]` — flat list of all APs

---

### get(ap_id)

Get an AP by ID (queries by ID filter).

```python
ap = client.aps.get("ap-uuid")
```

**Returns:** `dict` — AP details

**Raises:** `ResourceNotFoundError`

---

### update(venue_id, serial_number, **kwargs)

Update an AP.

```python
client.aps.update("venue-uuid", "AP-SERIAL", name="Lobby AP")
```

**Returns:** `dict`

---

### reboot(venue_id, serial_number)

Reboot an AP.

```python
client.aps.reboot("venue-uuid", "AP-SERIAL")
```

**Returns:** `dict` — operation status

---

### add_to_venue(venue_id, serial_number, name, ...)

Preprovision an AP to a venue.

```python
client.aps.add_to_venue("venue-uuid", "AP-SERIAL", name="New AP", description="Floor 2")
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `venue_id` | str | Yes | Venue ID |
| `serial_number` | str | Yes | AP serial number |
| `name` | str | Yes | AP name |
| `description` | str | No | Description |
| `model` | str | No | AP model |

**Returns:** `dict`

---

### remove_from_venue(venue_id, serial_number)

Remove an AP from a venue.

```python
client.aps.remove_from_venue("venue-uuid", "AP-SERIAL")
```

---

### add_to_group(venue_id, ap_group_id, serial_numbers)

Add APs to an AP group.

```python
client.aps.add_to_group("venue-uuid", "group-uuid", ["SERIAL1", "SERIAL2"])
```

**Returns:** `dict`

---

### get_clients(venue_id, serial_number=None, **kwargs)

Get clients connected to APs.

```python
clients = client.aps.get_clients("venue-uuid")
clients = client.aps.get_clients("venue-uuid", serial_number="AP-SERIAL")
```

**Returns:** `dict`

---

### get_radio_settings(venue_id, serial_number)

Get radio settings for an AP.

```python
settings = client.aps.get_radio_settings("venue-uuid", "AP-SERIAL")
```

**Returns:** `dict`

---

### update_radio_settings(venue_id, serial_number, settings)

Update radio settings.

```python
client.aps.update_radio_settings("venue-uuid", "AP-SERIAL", {"channelWidth": "40"})
```

**Returns:** `dict`

---

### get_statistics(venue_id, serial_number)

Get AP statistics.

```python
stats = client.aps.get_statistics("venue-uuid", "AP-SERIAL")
```

**Returns:** `dict`

---

### get_support_logs(venue_id, serial_number)

Request support log generation for an AP.

```python
response = client.aps.get_support_logs("venue-uuid", "AP-SERIAL")
```

**Returns:** Raw response object (use `response.json()` for download URL)

---

### get_venue_ap_management_vlan(venue_id)

Get AP management VLAN settings for a venue.

```python
vlan_settings = client.aps.get_venue_ap_management_vlan("venue-uuid")
```

**Returns:** `dict`

---

### update_venue_ap_management_vlan(venue_id, **kwargs)

Update AP management VLAN settings for a venue.

```python
client.aps.update_venue_ap_management_vlan("venue-uuid", vlanId=100, enabled=True)
```

**Returns:** `dict`

---

### get_ap_management_vlan(venue_id, ap_serial)

Get AP management VLAN settings for a specific AP.

```python
vlan_settings = client.aps.get_ap_management_vlan("venue-uuid", "AP-SERIAL")
```

**Returns:** `dict`

---

### update_ap_management_vlan(venue_id, ap_serial, **kwargs)

Update AP management VLAN settings for a specific AP.

```python
client.aps.update_ap_management_vlan("venue-uuid", "AP-SERIAL", vlanId=200)
```

**Returns:** `dict`
