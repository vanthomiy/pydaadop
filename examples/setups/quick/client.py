from examples.models.generic_model import GenericModel
from pydaadop.api_clients.client_api_factory import ClientFactory
import os

def example_usage():
    # Step 1: Initialize Client
    host = os.getenv("FAST_API_BASE_URL", "127.0.0.1")
    port = int(os.getenv("FAST_API_PORT", 8000))
    base_url = f"{host}:{port}"
    
    client = ClientFactory(base_url).get_read_client(GenericModel)
    
    # get display info
    print(client.get_display_info())

    # get query info
    print(client.get_query_info())



if __name__ == "__main__":
    example_usage()
