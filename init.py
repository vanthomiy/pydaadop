from datetime import datetime, timedelta
import os
from generic_model import GenericModel
from custom_model import CustomModel
from my_definition import MyDefinition
from pydaadop.api_clients.client_api_factory import ClientFactory

def init_database():
    # Step 1: Initialize Client
    host = os.getenv("FAST_API_BASE_URL_INTERNAL", "0.0.0.0")
    port = int(os.getenv("FAST_API_PORT", 8000))
    base_url = f"{host}:{port}"
    generic_model_client = ClientFactory(base_url).get_read_write_client(GenericModel)
    custom_model_client = ClientFactory(base_url).get_many_read_write_client(CustomModel)

    
    # Step 2: Insert data

    # Insert 10 items of GenericModel
    for i in range(10):
        # with i also iterate over the enum values to create a different value for each item
        definition = list(MyDefinition)[i % len(MyDefinition)]
        # Create a new item
        generic_item = GenericModel(str_value=str(i), int_value=i, float_value=i, test_enum=definition, date_value=datetime.now() + timedelta(days=i))
        # Insert the item one by one
        generic_model_client.insert(generic_item)
    
    # Insert 10 items of CustomModel
    custom_models = []
    for i in range(10):
        # with i also iterate over the enum values to create a different value for each item
        definition = list(MyDefinition)[i % len(MyDefinition)]
        # Create a new item
        custom_item = CustomModel(str_value=str(i), int_value=i, float_value=i, test_enum=definition, date_value=datetime.now() + timedelta(days=i))
        custom_models.append(custom_item)
    # Insert all items at once
    custom_model_client.insert_many(custom_models)


if __name__ == "__main__":
    init_database()