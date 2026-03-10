# WiFi Networks

Access via `client.wifi_networks` (or legacy alias `client.wlans`). See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list(query_data)

List WiFi networks.

```python
result = client.wifi_networks.list()
result = client.wifi_networks.list({"pageSize": 50, "page": 0})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### list_all(query_data)

Fetch all WiFi networks using auto-pagination.

```python
all_networks = client.wifi_networks.list_all()
```

**Returns:** `list[dict]`

---

### get(wlan_id)

Get a WiFi network by ID.

```python
network = client.wifi_networks.get("wlan-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(name, ssid, ...)

Create a new WiFi network.

```python
# WPA2-PSK
network = client.wifi_networks.create(
    name="Corp WiFi",
    ssid="CorpWiFi",
    security_type="wpa2-psk",
    passphrase="SecurePass123"
)

# Open
network = client.wifi_networks.create(name="Guest", ssid="Guest", security_type="open")

# Enterprise
network = client.wifi_networks.create(name="802.1X", ssid="SecureNet", security_type="wpa2-enterprise")
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | str | — | Network name |
| `ssid` | str | — | SSID (broadcast name) |
| `security_type` | str | "psk" | One of: `psk`, `wpa2-psk`, `wpa3-psk`, `wpa23mixed`, `open`, `owe`, `wpa2-enterprise`, `aaa`, `wpa3-enterprise` |
| `passphrase` | str \| None | None | WPA passphrase (required for PSK types) |
| `vlan_id` | int \| None | None | VLAN ID |
| `hidden` | bool | False | Hide SSID |
| `enabled` | bool | True | Enable network |
| `description` | str \| None | None | Description |
| `wlan_options` | dict \| None | None | Extra keys merged into `wlan` object |
| `advanced_options` | dict \| None | None | Extra keys merged into `wlan.advancedCustomization` |

**Returns:** `dict`

**Raises:** `ValueError` if `security_type` is unknown or passphrase missing for PSK

---

### update(wlan_id, **kwargs)

Update a WiFi network.

```python
client.wifi_networks.update("wlan-uuid", name="Updated Name")
```

**Returns:** `dict`

---

### delete(wlan_id)

Delete a WiFi network.

```python
client.wifi_networks.delete("wlan-uuid")
```

---

### list_venue_wlans(venue_id, ...)

List WiFi networks deployed in a specific venue.

```python
result = client.wifi_networks.list_venue_wlans("venue-uuid")
result = client.wifi_networks.list_venue_wlans("venue-uuid", search_string="Guest")
```

**Returns:** `dict`

---

### deploy_to_venue(wlan_id, venue_id, ...)

Deploy a WiFi network to a venue.

```python
client.wifi_networks.deploy_to_venue("wlan-uuid", "venue-uuid")
client.wifi_networks.deploy_to_venue("wlan-uuid", "venue-uuid", is_all_ap_groups=False)
```

**Returns:** `dict`

---

### undeploy_from_venue(wlan_id, venue_id)

Remove a WiFi network deployment from a venue.

```python
client.wifi_networks.undeploy_from_venue("wlan-uuid", "venue-uuid")
```

---

### get_venue_wlan_settings(wlan_id, venue_id)

Get deployment settings for a WiFi network in a venue.

```python
settings = client.wifi_networks.get_venue_wlan_settings("wlan-uuid", "venue-uuid")
```

**Returns:** `dict`

---

### update_venue_wlan_settings(wlan_id, venue_id, **kwargs)

Update deployment settings for a WiFi network in a venue.

```python
client.wifi_networks.update_venue_wlan_settings("wlan-uuid", "venue-uuid", vlanId=100)
```

**Returns:** `dict`

---

### get_radius_proxy_settings(wlan_id)

Get RADIUS server profile settings for a WiFi network.

```python
settings = client.wifi_networks.get_radius_proxy_settings("wlan-uuid")
```

**Returns:** `dict` — includes `enableAuthProxy`, `enableAccountingProxy`

---

### associate_dpsk_service(wlan_id, dpsk_service_id)

Associate a DPSK service with a WiFi network.

```python
client.wifi_networks.associate_dpsk_service("wlan-uuid", "dpsk-service-uuid")
```

**Returns:** `dict`
