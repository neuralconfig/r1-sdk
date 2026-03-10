# Venues

Access via `client.venues`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list()

List venues with optional filtering.

```python
result = client.venues.list()
result = client.venues.list(search_string="HQ", page_size=50, page=0, sort_field="name")
result = client.venues.list(data={"pageSize": 100, "page": 0})  # raw query dict
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `search_string` | str \| None | None | Filter venues by name |
| `page_size` | int | 100 | Results per page |
| `page` | int | 0 | Page number (0-based) |
| `sort_field` | str \| None | None | Field to sort by |
| `sort_order` | str | "ASC" | "ASC" or "DESC" |
| `data` | dict \| None | None | Raw query dict (overrides other params) |

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### list_all()

Fetch all venues using auto-pagination.

```python
all_venues = client.venues.list_all()
all_venues = client.venues.list_all(search_string="Branch")
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `search_string` | str \| None | None | Filter venues by name |
| `sort_field` | str \| None | None | Field to sort by |

**Returns:** `list[dict]` — flat list of all venues

---

### get(venue_id)

Get a venue by ID.

```python
venue = client.venues.get("venue-uuid")
```

**Returns:** `dict` — venue details

**Raises:** `ResourceNotFoundError` if not found

---

### create(name, address, ...)

Create a new venue.

```python
venue = client.venues.create(
    name="Branch Office",
    address={"street": "123 Main St", "city": "Austin", "state": "TX"},
    description="Regional branch",
    timezone="America/Chicago"
)
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | str | Yes | Venue name |
| `address` | dict | Yes | Address object |
| `description` | str | No | Description |
| `timezone` | str | No | Timezone string |

**Returns:** `dict` — created venue

---

### update(venue_id, **kwargs)

Update a venue.

```python
client.venues.update("venue-uuid", name="New Name", description="Updated")
```

**Returns:** `dict` — updated venue

**Raises:** `ResourceNotFoundError`

---

### delete(venue_id)

Delete a venue.

```python
client.venues.delete("venue-uuid")
```

**Raises:** `ResourceNotFoundError`

---

### get_aps(venue_id)

Get APs in a venue.

```python
aps = client.venues.get_aps("venue-uuid")
```

**Returns:** `dict` — APs in venue

---

### get_switches(venue_id, **kwargs)

Get switches in a venue (POST query).

```python
switches = client.venues.get_switches("venue-uuid")
```

**Returns:** `dict` — switches in venue

---

### get_wlans(venue_id, **kwargs)

Get WiFi networks deployed in a venue (POST query).

```python
wlans = client.venues.get_wlans("venue-uuid")
```

**Returns:** `dict` — WLANs in venue

---

### get_clients(venue_id, **kwargs)

Get clients connected in a venue (POST query).

```python
clients = client.venues.get_clients("venue-uuid")
```

**Returns:** `dict` — clients in venue
