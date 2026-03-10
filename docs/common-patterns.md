# Common Patterns

Shared concepts used across all R1 SDK modules.

## Authentication

### From config file

Create a `config.ini` in your project root:

```ini
[credentials]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
tenant_id = YOUR_TENANT_ID
region = na
```

```python
from r1_sdk import R1Client

client = R1Client.from_config()                          # defaults to config.ini
client = R1Client.from_config("path/to/config.ini")      # custom path
client = R1Client.from_config(section="staging")         # custom section
```

### From environment variables

```bash
export R1_CLIENT_ID=your_id
export R1_CLIENT_SECRET=your_secret
export R1_TENANT_ID=your_tenant
export R1_REGION=na  # na, eu, asia
```

```python
client = R1Client.from_env()
```

### Direct initialization

```python
client = R1Client(
    client_id="your_id",
    client_secret="your_secret",
    tenant_id="your_tenant",
    region="na"
)
```

### Regions

| Region | Value |
|--------|-------|
| North America | `na` |
| Europe | `eu` |
| Asia | `asia` |

## Pagination

### Single page: `list()`

Most modules have a `list()` method that returns one page of results:

```python
result = client.venues.list(page_size=50, page=0)
# result = {"data": [...], "total": 123, "page": 0, ...}

items = result["data"]
total = result["total"]
```

For modules using query-style pagination (APs, switches, etc.):

```python
result = client.aps.list({"pageSize": 100, "page": 0, "sortOrder": "ASC"})
```

### All pages: `list_all()`

Auto-paginates and returns a flat list of all items:

```python
all_venues = client.venues.list_all()
# Returns: [venue1, venue2, ...]  (flat list, all pages combined)
```

### Manual pagination with `paginate_query()`

The client exposes a generic pagination helper for POST `/query` endpoints:

```python
all_items = client.paginate_query("/some/endpoint/query", query_data={"sortField": "name"})
```

## Query Data Format

POST `/query` endpoints accept a standard query body:

```python
query_data = {
    "pageSize": 100,           # Items per page (default varies)
    "page": 0,                 # 0-based page index
    "sortField": "name",       # Field to sort by (optional)
    "sortOrder": "ASC",        # "ASC" or "DESC" (must be uppercase)
    "searchString": "office",  # Free-text search (optional)
    "filters": [               # Endpoint-specific filters (optional)
        {"type": "VENUE", "value": "venue-id-here"}
    ]
}
```

## Error Handling

All SDK errors inherit from `R1Error`:

```
R1Error                    # Base exception
  APIError                 # HTTP errors (has status_code, message, detail)
    AuthenticationError    # 401
    ResourceNotFoundError  # 404
    ValidationError        # 400
    RateLimitError         # 429
    ServerError            # 5xx
```

### Example

```python
from r1_sdk.exceptions import (
    R1Error, APIError, AuthenticationError,
    ResourceNotFoundError, ValidationError,
    RateLimitError, ServerError
)

try:
    venue = client.venues.get("nonexistent-id")
except ResourceNotFoundError:
    print("Venue not found")
except RateLimitError:
    print("Too many requests, slow down")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
except R1Error as e:
    print(f"SDK error: {e}")
```

### Auto-retry on 401

The client automatically retries once on HTTP 401 by refreshing the OAuth2 token. If the retry also fails, an `AuthenticationError` is raised.
