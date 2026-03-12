# External Identities

Access via `client.external_identities`. See [common patterns](../common-patterns.md) for auth and pagination.

This is a **read-only** module for querying identities sourced from external authentication providers.

## Methods

### query(filters)

Query external identities.

```python
result = client.external_identities.query({"pageSize": 50})
```

**Returns:** `dict` — paginated results

---

### list_all(**kwargs)

Fetch all external identities using auto-pagination.

```python
identities = client.external_identities.list_all()
```

**Returns:** `list[dict]`
