# create base fast api app
from fastapi import FastAPI

from fastapi.concurrency import asynccontextmanager
import uvicorn
from pydaadop.routes.base.base_read_route import BaseReadRouter
from examples.models.generic_model import GenericModel
from examples.models.custom_model import CustomModel

# add the needed base models
endpoint_models = [GenericModel, CustomModel]

routers = []

# create read routers for each model
for endpoint_model in endpoint_models:
    router = BaseReadRouter(endpoint_model)
    routers.append(router)

# Use lifespan to handle startup and shutdown events
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Ensure the OpenAPI schema is generated before modifying it
    schema = _app.openapi()

    # Dynamically create the model
    for _router in routers:
        schema = _router.create_openapi_schema(schema)

    # Set the modified schema back to app's OpenAPI schema
    _app.openapi_schema = schema

    yield  # Continue the lifespan

# Create FastAPI app and include the created routers
app = FastAPI(lifespan=lifespan)
[app.include_router(router.router) for router in routers]


if __name__ == "__main__":
    uvicorn.run(app)


