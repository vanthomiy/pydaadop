from fastapi import FastAPI

from ...routes.base.base_read_route import BaseReadRouter

from ..models.generic_model import GenericModel


app = FastAPI(title="Pydaadop Demo - Read Only")

# mount the read-only router at /generic
app.include_router(BaseReadRouter(GenericModel).router, prefix="/generic")


@app.get("/health")
def health():
    return {"status": "ok"}
