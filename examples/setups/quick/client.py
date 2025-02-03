from examples.models.generic_model import GenericModel
from pydaadop.api_clients.client_api_factory import ClientFactory

def example_usage():
    # Step 1: Initialize Client
    base_url = "http://localhost:8000"
    client = ClientFactory(base_url).get_read_client(GenericModel)
    
    # get display info
    print(client.get_display_info())

    # get query info
    print(client.get_query_info())



if __name__ == "__main__":
    example_usage()
