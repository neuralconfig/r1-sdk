# L3 ACL Policies

Access via `client.l3_acl_policies` (or legacy alias `client.l3acl`). See [common patterns](../common-patterns.md) for auth and pagination.

## Methods

### list(query_data)

List L3 ACL policies.

```python
result = client.l3_acl_policies.list()
result = client.l3_acl_policies.list({"pageSize": 50, "page": 0})
```

**Returns:** `dict` — `{"data": [...], "total": N, ...}`

---

### get(l3acl_policy_id)

Get an L3 ACL policy by ID.

```python
policy = client.l3_acl_policies.get("policy-uuid")
```

**Returns:** `dict`

**Raises:** `ResourceNotFoundError`

---

### create(name, l3_rules, ...)

Create a new L3 ACL policy.

```python
policy = client.l3_acl_policies.create(
    name="Block Social Media",
    l3_rules=[
        client.l3_acl_policies.create_rule(
            description="Block Facebook",
            priority=1,
            access="BLOCK",
            destination_enable_ip_subnet=True,
            destination_ip="157.240.0.0",
            destination_ip_mask="255.255.0.0"
        )
    ],
    default_access="ALLOW"
)
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | str | — | Policy name |
| `l3_rules` | list[dict] | — | List of L3 rules (max 128) |
| `description` | str \| None | None | Description |
| `default_access` | str | "BLOCK" | "ALLOW" or "BLOCK" |

**Returns:** `dict`

**Raises:** `ValueError` if rule count exceeds 128

---

### update(l3acl_policy_id, name, l3_rules, ...)

Update an L3 ACL policy (full replacement).

```python
client.l3_acl_policies.update("policy-uuid", name="Updated Policy", l3_rules=[...])
```

**Returns:** `dict`

---

### delete(l3acl_policy_id)

Delete an L3 ACL policy.

```python
client.l3_acl_policies.delete("policy-uuid")
```

**Returns:** `dict`

---

### create_rule(...) — Helper

Build an L3 rule dictionary for use with `create()` and `update()`. This is a helper that returns a dict, not an API call.

```python
rule = client.l3_acl_policies.create_rule(
    description="Allow DNS",
    priority=1,
    access="ALLOW",
    destination_enable_ip_subnet=True,
    destination_ip="8.8.8.8",
    destination_ip_mask="255.255.255.255",
    destination_port="53"
)
```

**Parameters:** `description`, `priority`, `access`, `source_enable_ip_subnet`, `source_ip`, `source_ip_mask`, `destination_enable_ip_subnet`, `destination_ip`, `destination_ip_mask`, `destination_port`

**Returns:** `dict` — rule definition
