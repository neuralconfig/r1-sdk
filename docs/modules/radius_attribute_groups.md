# RADIUS Attribute Groups

Access via `client.radius_attribute_groups`. See [common patterns](../common-patterns.md) for auth and pagination.

## Group Methods

### query(filters)

Query RADIUS attribute groups.

```python
result = client.radius_attribute_groups.query({"pageSize": 50})
```

**Returns:** `dict` — paginated results

---

### list_all(**kwargs)

Fetch all RADIUS attribute groups using auto-pagination.

```python
groups = client.radius_attribute_groups.list_all()
```

**Returns:** `list[dict]`

---

### get(group_id)

Get a RADIUS attribute group by ID.

```python
group = client.radius_attribute_groups.get("group-uuid")
```

**Returns:** `dict`

---

### create(name, attribute_assignments, **kwargs)

Create a RADIUS attribute group.

```python
group = client.radius_attribute_groups.create(
    "VLAN Assignment",
    attribute_assignments=[
        {"attributeId": "attr-uuid", "value": "100"}
    ]
)
```

**Returns:** `dict`

---

### update(group_id, **kwargs)

Update a RADIUS attribute group.

```python
client.radius_attribute_groups.update("group-uuid", name="Updated Name")
```

**Returns:** `dict`

---

### delete(group_id)

Delete a RADIUS attribute group.

```python
client.radius_attribute_groups.delete("group-uuid")
```

---

## Reference Data Methods

### list_attributes(**kwargs)

List available RADIUS attributes.

```python
attrs = client.radius_attribute_groups.list_attributes()
```

**Returns:** RADIUS attribute list

---

### list_vendors()

List RADIUS attribute vendors.

```python
vendors = client.radius_attribute_groups.list_vendors()
```

**Returns:** vendor list
