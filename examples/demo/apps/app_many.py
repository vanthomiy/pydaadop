from fastapi import FastAPI
from examples.models.custom_model import CustomModel
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter

app = FastAPI()

router = ManyReadWriteRouter(CustomModel)
app.include_router(router.router, prefix="/custom", tags=["custom"])


@app.get("/health")
def health():
    return {"status": "ok"}
