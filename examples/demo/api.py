from fastapi import FastAPI
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.models.base.base_mongo_model import BaseMongoModel


class DemoProduct(BaseMongoModel):
    name: str
    price: float

    @staticmethod
    def create_index():
        return ["name"]


app = FastAPI(title="Pydaadop Demo")
app.include_router(BaseReadWriteRouter(DemoProduct).router)

@app.get("/health")
def health():
    return {"status": "ok"}
