from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.routes.base.base_read_route import BaseReadRouter
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from pydaadop.routes.mcp import MCPRouter

from ..models.generic_model import GenericModel
from ..models.custom_model import CustomModel
from pydaadop.models.base.base_mongo_model import BaseMongoModel


class DemoProduct(BaseMongoModel):
    name: str
    price: float

    @staticmethod
    def create_index():
        return ["name"]


app = FastAPI(title="Pydaadop Demo")

# Read-only router for GenericModel (example of read-only API)
app.include_router(BaseReadRouter(GenericModel).router)

# Read-write router for DemoProduct
app.include_router(BaseReadWriteRouter(DemoProduct).router)

# Many read-write router for CustomModel
app.include_router(ManyReadWriteRouter(CustomModel).router)

# MCP router to expose model metadata
mcp = MCPRouter()
mcp.register(GenericModel)
mcp.register(DemoProduct)
mcp.register(CustomModel)
app.include_router(mcp.router)


@app.get("/health")
def health():
    return {"status": "ok"}
