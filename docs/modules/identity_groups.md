# Identity Groups

Access via `client.identity_groups`. See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list()

List all identity groups.

```python
groups = client.identity_groups.list()
```

**Returns:** `dict`

---

### list_all(**kwargs)

Fetch all identity groups using auto-pagination.

```python
all_groups = client.identity_groups.list_all()
```

**Returns:** `list[dict]`

---

### query(...)

Query identity groups with pagination and filtering.

```python
result = client.identity_groups.query(page=0, page_size=50)
result = client.identity_groups.query(dpsk_pool_id="pool-uuid")
result = client.identity_groups.query(certificate_template_id="cert-uuid")
```

**Parameters:** `page`, `page_size`, `certificate_template_id`, `dpsk_pool_id`, `policy_set_id`, `property_id`

**Returns:** `dict`

---

### get(group_id)

Get an identity group by ID.

```python
group = client.identity_groups.get("group-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(name, ...)

Create a new identity group.

```python
group = client.identity_groups.create(
    name="Employees",
    description="Employee identity group",
    dpsk_pool_id="pool-uuid"
)
```

**Parameters:** `name`, `description`, `dpsk_pool_id`, `certificate_template_id`, `policy_set_id`, `property_id`

**Returns:** `dict`

---

### update(group_id, **kwargs)

Update an identity group.

```python
client.identity_groups.update("group-uuid", name="Updated Group")
```

**Returns:** `dict`

---

### delete(group_id)

Delete an identity group.

```python
client.identity_groups.delete("group-uuid")
```

---

### associate_dpsk_pool(group_id, dpsk_pool_id)

Associate a DPSK pool with an identity group.

```python
client.identity_groups.associate_dpsk_pool("group-uuid", "pool-uuid")
```

**Returns:** `dict`

---

### associate_policy_set(group_id, policy_set_id)

Associate a policy set with an identity group.

```python
client.identity_groups.associate_policy_set("group-uuid", "policy-set-uuid")
```

**Returns:** `dict`
