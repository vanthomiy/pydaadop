# create base fast api app
from fastapi import FastAPI

import uvicorn
from src.pydaadop.routes.base.base_read_route import BaseReadRouter
from examples.models.generic_model import GenericModel
from examples.models.custom_model import CustomModel

# add the needed base models
endpoint_models = [GenericModel, CustomModel]

routers = []

# create read routers for each model
for endpoint_model in endpoint_models:
    router = BaseReadRouter(endpoint_model)
    routers.append(router)


# Create FastAPI app and include the created routers
app = FastAPI()
[app.include_router(router.router) for router in routers]


if __name__ == "__main__":
    uvicorn.run(app)


