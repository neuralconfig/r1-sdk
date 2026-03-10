# DPSK (Dynamic Pre-Shared Key)

Access via `client.dpsk`. See [common patterns](../common-patterns.md) for auth and pagination.

## Service Methods

### list_services(filters)

List DPSK services.

```python
services = client.dpsk.list_services()
services = client.dpsk.list_services({"pageSize": 50, "page": 0})
```

**Returns:** `list[dict]` — list of DPSK services

---

### get_service(pool_id)

Get a DPSK service by ID.

```python
service = client.dpsk.get_service("pool-uuid")
```

**Returns:** `dict`

---

### create_service(name, **kwargs)

Create a new DPSK service.

```python
service = client.dpsk.create_service("Employee DPSK", maxDevices=3, expirationDays=365)
```

**Returns:** `dict`

---

### update_service(pool_id, updates)

Update a DPSK service.

```python
client.dpsk.update_service("pool-uuid", {"name": "Updated DPSK", "maxDevices": 5})
```

**Returns:** `dict`

---

### delete_service(pool_id)

Delete a DPSK service.

```python
client.dpsk.delete_service("pool-uuid")
```

---

## Passphrase Methods

### list_passphrases(pool_id, filters)

List passphrases in a DPSK pool.

```python
passphrases = client.dpsk.list_passphrases("pool-uuid")
passphrases = client.dpsk.list_passphrases("pool-uuid", {"pageSize": 50})
```

**Returns:** `list[dict]`

---

### get_passphrase(pool_id, passphrase_id)

Get a specific passphrase.

```python
pp = client.dpsk.get_passphrase("pool-uuid", "passphrase-uuid")
```

**Returns:** `dict`

---

### create_passphrases(pool_id, passphrases)

Create new passphrases.

```python
result = client.dpsk.create_passphrases("pool-uuid", [
    {"userName": "john", "passphrase": "SecretKey1"},
    {"userName": "jane", "passphrase": "SecretKey2"}
])
```

**Returns:** `dict`

---

### update_passphrase(pool_id, passphrase_id, updates)

Update a passphrase.

```python
client.dpsk.update_passphrase("pool-uuid", "passphrase-uuid", {"userName": "updated_name"})
```

**Returns:** `dict`

---

### delete_passphrases(pool_id, passphrase_ids)

Delete passphrases from a pool.

```python
client.dpsk.delete_passphrases("pool-uuid", ["id1", "id2"])
```

---

### batch_update_passphrases(pool_id, updates)

Batch update multiple passphrases (PATCH).

```python
client.dpsk.batch_update_passphrases("pool-uuid", [
    {"id": "pp-id-1", "userName": "updated1"},
    {"id": "pp-id-2", "userName": "updated2"}
])
```

**Returns:** `dict`

---

## Device Methods

### list_devices(pool_id, passphrase_id)

List devices associated with a passphrase.

```python
devices = client.dpsk.list_devices("pool-uuid", "passphrase-uuid")
```

**Returns:** `list[dict]`

---

### add_devices(pool_id, passphrase_id, devices)

Add devices to a passphrase.

```python
client.dpsk.add_devices("pool-uuid", "passphrase-uuid", [
    {"macAddress": "AA:BB:CC:DD:EE:FF"}
])
```

**Returns:** `dict`

---

### update_devices(pool_id, passphrase_id, devices)

Update device associations (PATCH).

```python
client.dpsk.update_devices("pool-uuid", "passphrase-uuid", [
    {"macAddress": "AA:BB:CC:DD:EE:FF", "name": "Laptop"}
])
```

**Returns:** `dict`

---

### remove_devices(pool_id, passphrase_id, device_macs)

Remove devices from a passphrase.

```python
client.dpsk.remove_devices("pool-uuid", "passphrase-uuid", ["AA:BB:CC:DD:EE:FF"])
```

---

## Import/Export Methods

### import_passphrases_csv(pool_id, csv_content)

Import passphrases from CSV.

```python
with open("passphrases.csv") as f:
    result = client.dpsk.import_passphrases_csv("pool-uuid", f.read())
```

**Returns:** `dict`

---

### export_passphrases_csv(pool_id, filters)

Export passphrases to CSV.

```python
csv_text = client.dpsk.export_passphrases_csv("pool-uuid")
```

**Returns:** `str` — CSV content
