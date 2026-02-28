from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.routes.base.base_read_route import BaseReadRouter
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from pydaadop.routes.mcp import MCPRouter

from ..models.generic_model import GenericModel
from ..models.custom_model import CustomModel
from ..models.demo_product import DemoProduct
from ..routes.custom_demo_route import router as custom_demo_router
from pydaadop.relations.core import register_repo


# Create a tiny in-memory repo for demo use when MongoDB is not available.
class _InMemoryRepo:
    def __init__(self, items):
        # items should be model instances
        self._items = items

    async def get_many_by_ids(self, ids, projection=None):
        s = {
            str(getattr(item, "id", getattr(item, "_id", None))): item
            for item in self._items
        }
        out = []
        for i in ids:
            key = str(i)
            if key in s:
                out.append(s[key])
        return out


# Register a default empty demo repo for demoproduct so example routes don't
# crash when no Mongo instance is running. Tests or example code can replace
# this with a populated repo at runtime if desired.
register_repo("demoproduct", _InMemoryRepo([]))


app = FastAPI(title="Pydaadop Demo")

# Read-only router for GenericModel (example of read-only API)
# Include routers without an explicit prefix so the router's internal,
# model-derived prefix (e.g. '/demoproduct') is used. This keeps
# behavior consistent for tests that include routers without a prefix
# and for the demo app.
app.include_router(BaseReadRouter(GenericModel).router)

# Read-write router for DemoProduct
app.include_router(BaseReadWriteRouter(DemoProduct).router)

# Many read-write router for CustomModel
# Expose many-* endpoints at root so integration tests can call
# '/custom-insert-many' and '/custom-delete-many/'. Mounting with no
# external prefix ensures the final path matches test expectations.
app.include_router(ManyReadWriteRouter(CustomModel).router)

# MCP router to expose model metadata
mcp = MCPRouter()
mcp.register(GenericModel)
mcp.register(DemoProduct)
mcp.register(CustomModel)
app.include_router(mcp.router)

# Register example custom demo router
app.include_router(custom_demo_router)


@app.get("/health")
def health():
    return {"status": "ok"}
