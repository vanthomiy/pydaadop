from fastapi import FastAPI
import uvicorn
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.routes.many.many_read_write_route import ManyReadWriteRouter

from generic_model import GenericModel
from custom_model import CustomModel
import os

# Create FastAPI app
app = FastAPI()
# Include a base read write router of type GenericModel
app.include_router(BaseReadWriteRouter(GenericModel).router)
# Include a many read write router of type CustomModel
app.include_router(ManyReadWriteRouter(CustomModel).router)

# Run the app
if __name__ == "__main__":
    host = os.getenv("FAST_API_BASE_URL", "127.0.0.1")
    port = int(os.getenv("FAST_API_PORT", 8000))

    uvicorn.run(app, host=host, port=port)