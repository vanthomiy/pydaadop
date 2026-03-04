from fastapi import FastAPI

from ...routes.base.base_read_route import BaseReadRouter

from examples.models.demo_product import DemoProduct


app = FastAPI(title="Pydaadop Demo - Read Only")

# mount the read-only router at /generic
app.include_router(BaseReadRouter(DemoProduct).router, prefix="/generic")


@app.get("/health")
def health():
    return {"status": "ok"}
