# VLAN Pools

Access via `client.vlan_pools` (or legacy alias `client.vlans`). See [common patterns](../common-patterns.md) for auth and pagination.

## VLAN Pool Methods

### list_pools(query_data)

List VLAN pools.

```python
result = client.vlan_pools.list_pools()
result = client.vlan_pools.list_pools({"pageSize": 50, "page": 0})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### get_vlan_pool(vlan_pool_id)

Get a VLAN pool by ID.

```python
pool = client.vlan_pools.get_vlan_pool("pool-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create_vlan_pool(name, vlans, ...)

Create a new VLAN pool.

```python
pool = client.vlan_pools.create_vlan_pool(
    name="Office VLANs",
    vlans=[{"id": 100, "name": "Data"}, {"id": 200, "name": "Voice"}],
    description="Office VLAN pool"
)
```

**Returns:** `dict`

---

### update_vlan_pool(vlan_pool_id, **kwargs)

Update a VLAN pool.

```python
client.vlan_pools.update_vlan_pool("pool-uuid", name="Updated Pool")
```

**Returns:** `dict`

---

### delete_vlan_pool(vlan_pool_id)

Delete a VLAN pool.

```python
client.vlan_pools.delete_vlan_pool("pool-uuid")
```

---

## VLAN Pool Profile Methods

### list_profiles(query_data)

List VLAN pool profiles.

```python
result = client.vlan_pools.list_profiles()
```

**Returns:** `dict`

---

### get_vlan_pool_profile(profile_id)

Get a VLAN pool profile by ID.

```python
profile = client.vlan_pools.get_vlan_pool_profile("profile-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create_vlan_pool_profile(name, vlan_pool_id, ...)

Create a new VLAN pool profile.

```python
profile = client.vlan_pools.create_vlan_pool_profile(
    name="Branch Profile",
    vlan_pool_id="pool-uuid",
    description="Profile for branch offices"
)
```

**Returns:** `dict`

---

### update_vlan_pool_profile(profile_id, **kwargs)

Update a VLAN pool profile.

```python
client.vlan_pools.update_vlan_pool_profile("profile-uuid", name="Updated Profile")
```

**Returns:** `dict`

---

### delete_vlan_pool_profile(profile_id)

Delete a VLAN pool profile.

```python
client.vlan_pools.delete_vlan_pool_profile("profile-uuid")
```
