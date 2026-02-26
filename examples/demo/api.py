from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.routes.base.base_read_route import BaseReadRouter
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from pydaadop.routes.mcp import MCPRouter

from ..models.generic_model import GenericModel
from ..models.custom_model import CustomModel
from ..models.demo_product import DemoProduct


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
# Expose many-* endpoints under '/custom' so integration tests can call
# '/custom-insert-many' and '/custom-delete-many/'.
app.include_router(ManyReadWriteRouter(CustomModel).router, prefix="/custom")

# MCP router to expose model metadata
mcp = MCPRouter()
mcp.register(GenericModel)
mcp.register(DemoProduct)
mcp.register(CustomModel)
app.include_router(mcp.router)


@app.get("/health")
def health():
    return {"status": "ok"}
