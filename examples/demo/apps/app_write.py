from fastapi import FastAPI
from examples.models.demo_product import DemoProduct
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter

app = FastAPI()

router = BaseReadWriteRouter(DemoProduct)
app.include_router(router.router, prefix="/demoproduct", tags=["demoproduct"])


@app.get("/health")
def health():
    return {"status": "ok"}
