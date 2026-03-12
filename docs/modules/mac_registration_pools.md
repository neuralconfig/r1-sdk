# MAC Registration Pools

Access via `client.mac_registration_pools`. See [common patterns](../common-patterns.md) for auth and pagination.

> **Async mutations:** Mutation endpoints use the v1.1 async pattern — they return `202 Accepted` with a `requestId`. Read endpoints are synchronous.

## Pool Methods

### query(filters, page, size, **params)

Search MAC registration pools by criteria. Unlike most R1 query endpoints, pagination is via query params (`page`, `size`), not the request body. The body takes a `SearchDto` (with `dataOption`, `searchCriteriaList`).

```python
result = client.mac_registration_pools.query({"searchCriteriaList": []}, page=0, size=50)
pools = result.get("content", [])
```

**Returns:** `dict` — paginated results

---

### list_all(page_size, **kwargs)

Fetch all pools using GET with pagination.

```python
pools = client.mac_registration_pools.list_all()
```

**Returns:** `list[dict]`

---

### get(pool_id)

Get a pool by ID.

```python
pool = client.mac_registration_pools.get("pool-uuid")
```

**Returns:** `dict`

---

### create(identity_group_id, name, **kwargs)

Create a pool under an identity group (async 202).

```python
result = client.mac_registration_pools.create("group-uuid", "Guest MACs", description="Guest devices")
```

**Returns:** `dict` — async response with `requestId`

---

### update(pool_id, **kwargs)

Update a pool (v1.1 async).

```python
result = client.mac_registration_pools.update("pool-uuid", name="Updated Name")
```

**Returns:** `dict` — async response with `requestId`

---

### delete(pool_id)

Delete a pool (v1.1 async).

```python
result = client.mac_registration_pools.delete("pool-uuid")
```

**Returns:** `dict` — async response with `requestId`

---

## Registration Methods

### query_registrations(pool_id, filters, page, size, **params)

Search registrations in a pool. Like the pool query endpoint, pagination is via query params (`page`, `size`), not the request body.

```python
result = client.mac_registration_pools.query_registrations("pool-uuid", {}, page=0, size=50)
```

**Returns:** `dict` — paginated results

---

### list_all_registrations(pool_id, page_size, **kwargs)

Fetch all registrations in a pool via GET with pagination.

```python
regs = client.mac_registration_pools.list_all_registrations("pool-uuid")
```

**Returns:** `list[dict]`

---

### create_registration(pool_id, mac_address, **kwargs)

Create a MAC registration (v1.1 async).

```python
result = client.mac_registration_pools.create_registration("pool-uuid", "AA-BB-CC-DD-EE-FF")
```

**Returns:** `dict` — async response with `requestId`

---

### update_registration(pool_id, reg_id, **kwargs)

Update a registration (v1.1 async).

```python
result = client.mac_registration_pools.update_registration("pool-uuid", "reg-uuid", name="Laptop")
```

**Returns:** `dict` — async response with `requestId`

---

### delete_registration(pool_id, reg_id)

Delete a registration (v1.1 async).

```python
result = client.mac_registration_pools.delete_registration("pool-uuid", "reg-uuid")
```

**Returns:** `dict` — async response with `requestId`

---

### delete_registrations(pool_id, reg_ids)

Bulk delete registrations (v1.1 async).

```python
result = client.mac_registration_pools.delete_registrations("pool-uuid", ["id1", "id2"])
```

**Returns:** `dict` — async response with `requestId`

---

### import_csv(pool_id, csv_bytes)

Import registrations from CSV (v1.1 async, multipart).

```python
with open("macs.csv", "rb") as f:
    result = client.mac_registration_pools.import_csv("pool-uuid", f.read())
```

**Returns:** `dict` — async response with `requestId`

---

## Policy Set Association Methods

### associate_policy_set(pool_id, policy_set_id)

Associate a policy set with a pool (async 202).

```python
result = client.mac_registration_pools.associate_policy_set("pool-uuid", "ps-uuid")
```

**Returns:** `dict`

---

### remove_policy_set(pool_id, policy_set_id)

Remove a policy set association (async 202).

```python
result = client.mac_registration_pools.remove_policy_set("pool-uuid", "ps-uuid")
```

**Returns:** `dict`

---

## API Notes

- `POST /macRegistrationPools/query` returns 500 (server bug). Use `list_all()` which calls `GET /macRegistrationPools` with pagination instead.
- Both `query()` and `query_registrations()` use query param pagination (`page`, `size`) unlike most R1 POST `/query` endpoints which put pagination in the body.
