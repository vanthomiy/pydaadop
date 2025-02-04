# create base fast api app
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from src.deriven_core.routes.bulk.bulk_read_write_route import BulkReadWriteRouter
from tests.models.TestModel import TestModel, TestModel2

# Allow CORS
origins = [
    "http://localhost:5000",  # Add your Blazor app URL here
    "http://localhost:8000",   # Example: allow FastAPI itself if needed
    # Add other origins as necessary
]

# map endpoints to routers changes
endpoint_models = [TestModel, TestModel2]

routers = []

# add routers to app
for endpoint_model in endpoint_models:
    router = BulkReadWriteRouter(endpoint_model)
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

# Create FastAPI app and assign lifespan context manager
app = FastAPI(lifespan=lifespan)
[app.include_router(router.router) for router in routers]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],     # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers
)

if __name__ == "__main__":
    uvicorn.run(app, log_level="info")


