import os
from pydaadop.models.base.base_mongo_model import BaseMongoModel
from pydaadop.api_clients.client_api_factory import ClientFactory

def init_database():
        # Step 1: Initialize Client
    host = os.getenv("FAST_API_BASE_URL_INTERNAL", "0.0.0.0")
    port = int(os.getenv("FAST_API_PORT", 8000))
    base_url = f"{host}:{port}"

    client = ClientFactory(base_url).get_read_write_client(BaseMongoModel)

    item = BaseMongoModel()

    client.insert(item)

if __name__ == "__main__":
    init_database()