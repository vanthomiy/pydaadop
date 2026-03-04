from fastapi import FastAPI
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter
from examples.models.demo_product import DemoProduct

app = FastAPI()

router = ManyReadWriteRouter(DemoProduct)
app.include_router(router.router, prefix="/demoproduct", tags=["demoproduct"])


@app.get("/health")
def health():
    return {"status": "ok"}
