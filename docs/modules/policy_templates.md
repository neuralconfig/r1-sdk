# Policy Templates

Access via `client.policy_templates`. See [common patterns](../common-patterns.md) for auth and pagination.

> **ID types:** Template IDs are `int` (int64). Policy IDs are `str` (UUID).

## Template Methods

### query_templates(filters)

Query policy templates.

```python
result = client.policy_templates.query_templates({"pageSize": 50})
templates = result.get("data", [])
```

**Returns:** `dict` — paginated results

---

### list_all_templates(**kwargs)

Fetch all policy templates using auto-pagination.

```python
templates = client.policy_templates.list_all_templates()
```

**Returns:** `list[dict]`

---

### get_template(template_id)

Get a policy template by ID.

```python
template = client.policy_templates.get_template(200)
```

**Returns:** `dict`

---

### list_template_attributes(template_id)

List attributes for a policy template.

```python
attrs = client.policy_templates.list_template_attributes(200)
```

**Returns:** `list`

---

## Policy Query Methods

### query_policies(template_id, filters)

Query policies within a template.

```python
result = client.policy_templates.query_policies(200, {"pageSize": 50})
policies = result.get("data", [])
```

**Returns:** `dict` — paginated results

---

### list_all_policies(template_id, **kwargs)

Fetch all policies for a template using auto-pagination.

```python
policies = client.policy_templates.list_all_policies(200)
```

**Returns:** `list[dict]`

---

## Policy CRUD Methods

### get_policy(template_id, policy_id)

Get a policy by ID.

```python
policy = client.policy_templates.get_policy(200, "policy-uuid")
```

**Returns:** `dict`

---

### create_policy(template_id, name, policy_type, description, on_match_response, **kwargs)

Create a policy within a template. Uses a synchronous content-type header to get a 201 response instead of 202.

```python
# RADIUS policy (template 200)
policy = client.policy_templates.create_policy(
    200, "Guest RADIUS", "RADIUS",
    on_match_response="rag-uuid"
)

# DPSK policy (template 100)
policy = client.policy_templates.create_policy(
    100, "Guest DPSK", "DPSK",
    on_match_response="rag-uuid"
)
```

> **Note:** `on_match_response` (RADIUS attribute group ID) is required for RADIUS and DPSK policies despite the OpenAPI spec marking it optional. Omitting it results in a policy that cannot be assigned.

**Returns:** `dict` — created policy details

---

### update_policy(template_id, policy_id, **kwargs)

Update a policy.

```python
client.policy_templates.update_policy(200, "policy-uuid", name="Updated Name")
```

**Returns:** `dict`

---

### delete_policy(template_id, policy_id)

Delete a policy.

```python
client.policy_templates.delete_policy(200, "policy-uuid")
```
