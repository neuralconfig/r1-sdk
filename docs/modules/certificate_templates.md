# Certificate Templates

Access via `client.certificate_templates`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### query(query_data)

Query certificate templates with pagination.

```python
result = client.certificate_templates.query()
result = client.certificate_templates.query({"pageSize": 50})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### get(template_id)

Get a certificate template by ID.

```python
template = client.certificate_templates.get("template-uuid")
```

**Returns:** `dict`

---

### get_for_wifi_network(wlan_id)

Get the certificate template linked to a WiFi network. Queries all templates and returns the one whose `networkIds` contains the given WLAN ID.

```python
template = client.certificate_templates.get_for_wifi_network("wlan-uuid")
if template:
    print(template["name"])
```

**Returns:** `dict | None` — matching template, or `None` if not found
