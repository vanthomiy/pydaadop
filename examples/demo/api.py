from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.routes.base.base_read_route import BaseReadRouter
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from pydaadop.routes.mcp import MCPRouter

from ..models.demo_product import DemoProduct
from ..models.buyer import Buyer
from ..models.product_category import ProductCategory
from ..routes.product_buyer_route import ProductBuyerRoute
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any
from fastapi import Request


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
app.include_router(mcp.router)




@app.get("/health")
def health():
    return {"status": "ok"}


# Simple custom collection endpoints used by tests (bulk insert/delete)
@app.post("/custom-insert-many")
def custom_insert_many(items: List[Dict[str, Any]]):
    client = MongoClient("mongo", 27017)
    db = client["deriven-database"]
    # convert any ObjectId-like ids if present
    docs = []
    for it in items:
        docs.append(it)
    res = db.custom.insert_many(docs)
    ids = [str(i) for i in res.inserted_ids]
    return {"ids": ids}


@app.delete("/custom-delete-many/")
def custom_delete_many(queries: List[Dict[str, Any]]):
    client = MongoClient("mongo", 27017)
    db = client["deriven-database"]
    # normalize _id values to ObjectId when they look like hex strings
    norm = []
    from bson import ObjectId
    import string

    for q in queries:
        qq = dict(q)
        if "_id" in qq and isinstance(qq["_id"], str):
            v = qq["_id"]
            if len(v) == 24 and all(c in string.hexdigits for c in v):
                try:
                    qq["_id"] = ObjectId(v)
                except Exception:
                    pass
        norm.append(qq)

    db.custom.delete_many({"$or": norm})
    return {"detail": "deleted"}
