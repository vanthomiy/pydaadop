from fastapi import FastAPI
import uvicorn
from src.pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from src.pydaadop.routes.base.base_read_route import BaseReadRouter
from src.pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from src.pydaadop.routes.mcp import MCPRouter

from examples.models.demo_product import DemoProduct
from examples.models.buyer import Buyer
from examples.models.product_category import ProductCategory
from examples.routes.product_buyer_route import ProductBuyerRoute
from examples.models.product_buyer_display import ProductBuyerDisplay


product_buyer_router = ProductBuyerRoute()

app = FastAPI(title="Pydaadop Demo")

# Read-only router for GenericModel (example of read-only API)
# Include routers without an explicit prefix so the router's internal,
# model-derived prefix (e.g. '/demoproduct') is used. This keeps
# behavior consistent for tests that include routers without a prefix
# and for the demo app.
app.include_router(ManyReadWriteRouter(Buyer).router)

app.include_router(ManyReadWriteRouter(ProductCategory).router)

# Read-write router for DemoProduct
app.include_router(ManyReadWriteRouter(DemoProduct).router)

# Register example custom demo router
app.include_router(product_buyer_router.router)

# MCP router to expose model metadata
mcp = MCPRouter()
mcp.register(Buyer)
mcp.register(DemoProduct)
mcp.register(ProductCategory)
mcp.register(ProductBuyerDisplay)
app.include_router(mcp.router)




@app.get("/health")
def health():
    return {"status": "ok"}


# Run the app
if __name__ == "__main__":
    uvicorn.run(app)