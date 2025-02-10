from fastapi import FastAPI
import uvicorn
from pydaadop.routes.base.base_read_write_route import BaseReadWriteRouter
from pydaadop.models.base.base_mongo_model import BaseMongoModel

# Create FastAPI app
app = FastAPI()
# Include a base read router of type BaseMongoModel
app.include_router(BaseReadWriteRouter(BaseMongoModel).router)

# Run the app
if __name__ == "__main__":
    uvicorn.run(app)