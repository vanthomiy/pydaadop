# pydaadop

> Streamline your Python projects with MongoDB, FastAPI, and Pydantic — simplifying setup and scalability.

[![CI](https://github.com/vanthomiy/pydaadop/actions/workflows/ci.yml/badge.svg)](https://github.com/vanthomiy/pydaadop/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydaadop)](https://pypi.org/project/pydaadop/)
[![Python](https://img.shields.io/pypi/pyversions/pydaadop)](https://pypi.org/project/pydaadop/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

**Pydaadop** generates production-ready FastAPI routes, MongoDB schemas, and query infrastructure from plain Pydantic models. Define your data once — get a full CRUD API, smart filtering, sorting, paging, and an optional MCP (Model Context Protocol) endpoint for LLM-friendly introspection.

### Architecture

```
Pydantic Model
    │
    ▼
BaseMongoModel ──► BaseRepository ──► MongoDB collection
    │
    ▼
BaseReadService / BaseReadWriteService
    │
    ▼
BaseReadRouter / BaseReadWriteRouter / ManyReadWriteRouter ──► FastAPI app
    │
    ▼
MCPRouter (optional) ──► /_mcp/context  (LLM introspection)
```

---

## Installation

```bash
pip install pydaadop
```

Requires Python ≥ 3.10.

### Development install

```bash
git clone https://github.com/vanthomiy/pydaadop.git
cd pydaadop
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Define a model

```python
from typing import List, Literal, Optional
from pydaadop.models.base.base_mongo_model import BaseMongoModel

class Product(BaseMongoModel):
    name: str
    price: float
    category: Optional[Literal["electronics", "clothing", "food"]] = None

    @staticmethod
    def create_index() -> List[str]:
        return ["name"]   # unique index fields
```

### 2. Mount the router

```python
from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter

app = FastAPI()
app.include_router(BaseReadWriteRouter(Product).router)
```

### 3. Set environment variables

```bash
export MONGO_CONNECTION_STRING="mongodb://user:pass@localhost:27017"
# or supply individual components:
# export MONGODB_USER=user
# export MONGODB_PASS=pass
# export MONGO_BASE_URL=localhost
# export MONGO_PORT=27017
```

### 4. Run

```bash
uvicorn myapp:app --reload
```

Generated endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/product/` | List all (filtering, sorting, paging, search) |
| `GET` | `/product/item/` | Get single item by index key |
| `GET` | `/product/exists/` | Check if item exists |
| `GET` | `/product/select/` | Project a single field |
| `GET` | `/product/display-info/query/` | Filterable / sortable field metadata |
| `GET` | `/product/display-info/item/` | Item count for a filter |
| `POST` | `/product/` | Create item |
| `PUT` | `/product/` | Upsert item |
| `DELETE` | `/product/` | Delete item by index key |

---

## MCP — Model Context Protocol

The `MCPRouter` exposes machine-readable metadata optimised for LLM agents and automation tools.

### What is MCP?

The **Model Context Protocol** is a lightweight JSON convention that describes the data models and REST operations of a service in a structured, discoverable way.  LLMs can query `/_mcp/context` to learn:
- What models exist and what fields they have
- Which fields are filterable / sortable
- What allowed values exist for enum / literal fields
- What CRUD operations are available and at which paths

This removes the need for an LLM to parse OpenAPI YAML or browse documentation.

### Why does it exist?

Traditional REST documentation (OpenAPI, Swagger) is designed for *human* developers.  MCP is designed for *machine* consumers:
- Compact, structured JSON with no prose noise
- Explicit `allowed_values` for enum fields (no schema `$ref` chase)
- Flat list of operations with a single `method + path + description` tuple
- Versioned via `schema_version` so agents can adapt

### Adding MCP to your app

```python
from fastapi import FastAPI
from pydaadop.routes.mcp import MCPRouter
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter

app = FastAPI()

# Standard REST routes
app.include_router(BaseReadWriteRouter(Product).router)

# MCP introspection
mcp = MCPRouter()
mcp.register(Product)
app.include_router(mcp.router)
```

### MCP endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/_mcp/context` | Full context document (models + operations) |
| `GET` | `/_mcp/models` | List of registered model names |
| `GET` | `/_mcp/models/{name}` | Detailed metadata for one model |

### Example: `GET /_mcp/context`

```json
{
  "schema_version": "1.0",
  "models": [
    {
      "name": "Product",
      "collection": "Product",
      "index_fields": ["name"],
      "fields": [
        {"name": "name", "type": "str", "required": true, "allowed_values": null},
        {"name": "price", "type": "float", "required": true, "allowed_values": null},
        {"name": "category", "type": "str", "required": false,
         "allowed_values": ["electronics", "clothing", "food"]}
      ],
      "filter_fields": ["category"],
      "sort_fields": ["name", "price", "category"]
    }
  ],
  "operations": [
    {"method": "GET",    "path": "/product/",        "description": "List all items with filtering, sorting, paging"},
    {"method": "POST",   "path": "/product/",        "description": "Create a new item"},
    {"method": "PUT",    "path": "/product/",        "description": "Update an existing item"},
    {"method": "DELETE", "path": "/product/",        "description": "Delete an item by index key"}
  ]
}
```

### How LLMs should interact with MCP

1. **Discovery**: `GET /_mcp/context` to learn everything in one request.
2. **Field lookup**: Check `allowed_values` before building filter queries.
3. **Operations**: Use `method + path` to construct requests — no schema parsing required.
4. **Model details**: `GET /_mcp/models/{name}` for focused metadata when full context is large.

---

## Docker

### Docker Compose (local dev)

```bash
cp tests/example.env .env
docker compose up
```

The `docker-compose.yml` starts a MongoDB container.  Configure your app via environment variables in `.env`.

### Dockerfile (custom app)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["uvicorn", "myapp:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Release Process

Releases are published to PyPI automatically when a Git tag is pushed.

```bash
# 1. Bump version in pyproject.toml
# 2. Commit the version bump
git commit -am "chore: bump version to 1.2.3"
# 3. Tag the release
git tag v1.2.3
git push origin v1.2.3
```

The `.github/workflows/workflow.yml` workflow will:
1. Verify the tag version matches `pyproject.toml`
2. Build the distribution
3. Publish to PyPI using trusted publishing (OIDC — no long-lived token stored in secrets)

> ⚠️ Configure the `pypi` environment in GitHub repository settings and enable trusted publishing on PyPI before the first release.

---

## Testing

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

The test suite covers:
- Unit tests for `BaseMongoModel`, `BaseQuery` helpers, and `env_manager`
- Integration tests for FastAPI routes using mocked repositories
- MCP route tests
- Edge-case tests (empty models, invalid configs, range / search extraction)

---

## Limitations

- MongoDB is the only supported database backend.
- All models must inherit from `BaseMongoModel`.
- `create_index()` must return at least one field name.
- MCP `schema_version` is currently fixed at `"1.0"`.

---

## License

MIT © [vanthomiy](https://github.com/vanthomiy)

