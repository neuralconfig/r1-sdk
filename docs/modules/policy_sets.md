# Policy Sets

Access via `client.policy_sets`. See [common patterns](../common-patterns.md) for auth and pagination.

## Policy Set Methods

### query(filters)

Query policy sets.

```python
result = client.policy_sets.query({"pageSize": 50})
```

**Returns:** `dict` — paginated results

---

### list_all(**kwargs)

Fetch all policy sets using auto-pagination.

```python
sets = client.policy_sets.list_all()
```

**Returns:** `list[dict]`

---

### get(policy_set_id)

Get a policy set by ID.

```python
ps = client.policy_sets.get("ps-uuid")
```

**Returns:** `dict`

---

### create(name, description, **kwargs)

Create a new policy set.

```python
ps = client.policy_sets.create("Guest Policy", description="Policies for guest access")
```

**Returns:** `dict`

---

### update(policy_set_id, **kwargs)

Update a policy set.

```python
client.policy_sets.update("ps-uuid", name="Updated Name")
```

**Returns:** `dict`

---

### delete(policy_set_id)

Delete a policy set.

```python
client.policy_sets.delete("ps-uuid")
```

---

## Prioritized Policy Methods

### list_policies(policy_set_id)

List prioritized policies in a set.

```python
policies = client.policy_sets.list_policies("ps-uuid")
```

**Returns:** `list[dict]`

---

### add_policy(policy_set_id, policy_id, **kwargs)

Add a policy to a set.

```python
client.policy_sets.add_policy("ps-uuid", "policy-uuid", priority=1)
```

**Returns:** `dict`

---

### remove_policy(policy_set_id, policy_id)

Remove a policy from a set.

```python
client.policy_sets.remove_policy("ps-uuid", "policy-uuid")
```

---

## Assignment Methods

### get_assignments(policy_set_id)

Get assignments for a policy set.

```python
assignments = client.policy_sets.get_assignments("ps-uuid")
```

**Returns:** `dict`
