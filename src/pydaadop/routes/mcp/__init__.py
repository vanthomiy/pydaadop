"""
MCP (Model Context Protocol) route implementation for Pydaadop.

Exposes structured, machine-readable metadata about registered models and their
available operations so that LLMs and other automated agents can query and
interact with the API without prior knowledge of the schema.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from fastapi import APIRouter
from pydantic import BaseModel

from ...models.base import BaseMongoModel
from ...queries.base.base_query import BaseQuery


# ── Response schemas ──────────────────────────────────────────────────────────

class MCPFieldInfo(BaseModel):
    """Metadata for a single model field."""

    name: str
    type: str
    required: bool
    allowed_values: Optional[List[Any]] = None
    description: Optional[str] = None


class MCPModelInfo(BaseModel):
    """Metadata for a single Pydantic / MongoDB model."""

    name: str
    collection: str
    index_fields: List[str]
    fields: List[MCPFieldInfo]
    filter_fields: List[str]
    sort_fields: List[str]


class MCPOperationInfo(BaseModel):
    """Description of a REST operation exposed for a model."""

    method: str
    path: str
    description: str


class MCPContext(BaseModel):
    """
    Full MCP context document.

    This is the top-level object returned by ``GET /_mcp/context``.
    """

    schema_version: str = "1.0"
    models: List[MCPModelInfo]
    operations: List[MCPOperationInfo]


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_model_info(model: Type[BaseMongoModel]) -> MCPModelInfo:
    """Build an :class:`MCPModelInfo` for *model*."""
    from typing import get_type_hints

    hints = get_type_hints(model)
    fields: List[MCPFieldInfo] = []

    for field_name, annotation in hints.items():
        field_type, _selectable = BaseQuery._get_type(annotation)
        if field_type is None:
            continue
        allowed = BaseQuery._get_allowed_values(annotation)
        pydantic_field = model.model_fields.get(field_name)
        required = pydantic_field is not None and pydantic_field.is_required()
        fields.append(
            MCPFieldInfo(
                name=field_name,
                type=field_type.__name__,
                required=required,
                allowed_values=allowed,
                description=pydantic_field.description if pydantic_field else None,
            )
        )

    filter_fields = list(BaseQuery.get_fields_of_model(model, only_selectable=True).keys())
    sort_fields = list(BaseQuery.get_fields_of_model(model, only_selectable=False).keys())

    return MCPModelInfo(
        name=model.__name__,
        collection=model.__name__,
        index_fields=model.create_index(),
        fields=fields,
        filter_fields=filter_fields,
        sort_fields=sort_fields,
    )


def _build_operations(model: Type[BaseMongoModel], prefix: str) -> List[MCPOperationInfo]:
    """Return the standard CRUD operations for *model*."""
    base = prefix.rstrip("/")
    return [
        MCPOperationInfo(method="GET", path=f"{base}/", description="List all items with filtering, sorting, paging"),
        MCPOperationInfo(method="GET", path=f"{base}/item/", description="Get a single item by index key"),
        MCPOperationInfo(method="GET", path=f"{base}/exists/", description="Check if an item exists"),
        MCPOperationInfo(method="GET", path=f"{base}/select/", description="List items projecting a single field"),
        MCPOperationInfo(method="GET", path=f"{base}/display-info/query/", description="Get filterable/sortable field metadata"),
        MCPOperationInfo(method="GET", path=f"{base}/display-info/item/", description="Get item count for a filter"),
        MCPOperationInfo(method="POST", path=f"{base}/", description="Create a new item"),
        MCPOperationInfo(method="PUT", path=f"{base}/", description="Update an existing item"),
        MCPOperationInfo(method="DELETE", path=f"{base}/", description="Delete an item by index key"),
    ]


# ── Router factory ────────────────────────────────────────────────────────────

class MCPRouter:
    """
    A lightweight router that exposes MCP metadata for one or more models.

    Usage::

        app = FastAPI()
        mcp = MCPRouter()
        mcp.register(MyModel)
        app.include_router(mcp.router)

    The router adds the following endpoints:

    * ``GET /_mcp/context``  – full context document (models + operations)
    * ``GET /_mcp/models``   – list of model names
    * ``GET /_mcp/models/{name}`` – metadata for a single model
    """

    def __init__(self) -> None:
        self.router = APIRouter(prefix="/_mcp", tags=["MCP"])
        self._models: Dict[str, Type[BaseMongoModel]] = {}
        self._setup_routes()

    def register(self, model: Type[BaseMongoModel]) -> None:
        """Register a model so it is included in MCP context responses."""
        self._models[model.__name__] = model

    def _setup_routes(self) -> None:
        router = self.router

        @router.get("/context", response_model=MCPContext, summary="Full MCP context")
        async def get_context() -> MCPContext:
            """
            Return the full Model Context Protocol document.

            This endpoint is the primary entry-point for LLMs and automated agents.
            It lists every registered model together with its fields, index keys,
            filterable/sortable attributes, and the REST operations available for it.
            """
            models_info: List[MCPModelInfo] = []
            operations_info: List[MCPOperationInfo] = []
            for model in self._models.values():
                models_info.append(_build_model_info(model))
                prefix = f"/{model.__name__.lower()}"
                operations_info.extend(_build_operations(model, prefix))
            return MCPContext(models=models_info, operations=operations_info)

        @router.get("/models", response_model=List[str], summary="List registered model names")
        async def list_models() -> List[str]:
            """Return the names of all models registered with this MCP router."""
            return list(self._models.keys())

        @router.get("/models/{name}", response_model=MCPModelInfo, summary="Get metadata for a single model")
        async def get_model(name: str) -> MCPModelInfo:
            """
            Return detailed metadata for the model identified by *name*.

            Raises 404 if the model is not registered.
            """
            from fastapi import HTTPException

            model = self._models.get(name)
            if model is None:
                raise HTTPException(status_code=404, detail=f"Model '{name}' not found")
            return _build_model_info(model)
