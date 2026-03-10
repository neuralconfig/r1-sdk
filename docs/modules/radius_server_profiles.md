# RADIUS Server Profiles

Access via `client.radius_server_profiles`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list()

List all RADIUS server profiles.

```python
profiles = client.radius_server_profiles.list()
```

**Returns:** `list[dict]`

---

### query(query_data)

Query RADIUS server profiles with pagination.

```python
result = client.radius_server_profiles.query()
result = client.radius_server_profiles.query({"pageSize": 50, "page": 0})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### get(profile_id)

Get a RADIUS server profile by ID.

```python
profile = client.radius_server_profiles.get("profile-uuid")
```

**Returns:** `dict` — includes server IP, port, and linked WiFi networks

---

### get_for_wifi_network(wlan_id)

Get RADIUS profiles linked to a specific WiFi network. Queries all profiles and filters by `wifiNetworkIds`.

```python
result = client.radius_server_profiles.get_for_wifi_network("wlan-uuid")
# result = {"AUTHENTICATION": [...], "ACCOUNTING": [...]}
```

**Returns:** `dict` — keys `AUTHENTICATION` and `ACCOUNTING`, each a list of matching profiles
