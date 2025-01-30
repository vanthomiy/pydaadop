from src.deriven_core.api_clients.client_api_factory import ClientFactory
from tests.models.TestModel import TestModel, TestEnum
from datetime import datetime

def test_client_endpoints():
    # Step 1: Initialize Client
    base_url = "http://localhost:8000"
    client = ClientFactory(base_url).get_many_read_write_client(TestModel)

    # Step 2: Test Insert Operation (Create Single Item)
    new_item = TestModel(
        str_value=1.23,
        int_value=123,
        float_value=456.78,
        date_value=datetime.now(),
        test_enum=TestEnum.A
    )
    try:
        inserted_item = client.insert(new_item)
        assert inserted_item.id is not None, "Insert failed: ID is None"
        print(f"Insert successful: {inserted_item}")
    except Exception as e:
        print(f"Insert failed: {e}")

    # Step 3: Test Get All Items (Read)
    all_items = client.get_all()
    assert isinstance(all_items, list), "Get all failed: Returned data is not a list"
    print(f"Get all successful: Found {len(all_items)} items")

    # Step 4: Test Get Single Item (Read)
    filter_query = {"str_value": 1.23, "int_value": 123}
    try:
        fetched_item = client.get(filter_query)
        assert fetched_item.id == inserted_item.id, "Get single failed: IDs do not match"
        print(f"Get single successful: {fetched_item}")
    except Exception as e:
        print(f"Get single failed: {e}")

    # Step 5: Test Update Operation (Update Single Item)
    fetched_item.int_value = 456
    try:
        updated_item = client.update(fetched_item)
        assert updated_item.int_value == 456, "Update failed: Value did not update"
        print(f"Update successful: {updated_item}")
    except Exception as e:
        print(f"Update failed: {e}")

    # Step 6: Test Insert Many Items
    new_items = [
        TestModel(str_value=2.34, int_value=234, float_value=123.45, date_value=datetime.now(), test_enum=TestEnum.B),
        TestModel(str_value=3.45, int_value=345, float_value=678.90, date_value=datetime.now(), test_enum=TestEnum.C)
    ]
    try:
        insert_many_response = client.insert_many(new_items)
        ids = insert_many_response["ids"]
        assert len(ids) == len(new_items), "Insert many failed"
        print(f"Insert many successful: {insert_many_response}")
    except Exception as e:
        print(f"Insert many failed: {e}")

    # Step 7: Test Update Many Items
    items_to_update = client.get_all()
    for item in items_to_update:
        item.int_value += 100  # Update values
    try:
        update_many_response = client.update_many(items_to_update)
        assert len(update_many_response.get("ids", [])) == len(items_to_update), "Update many failed"
        print(f"Update many successful: {update_many_response}")
    except Exception as e:
        print(f"Update many failed: {e}")

    # Step 8: Test Delete Operation (Delete Single Item)
    client.delete(items_to_update[0].model_dump_keys())  # Pass the model instance directly
    try:
        client.get(items_to_update[0].model_dump())  # If needed, use model_dump() to query
        assert False, "Delete failed: Item still exists"
    except Exception as e:
        print(f"Delete successful: {inserted_item.id} was deleted")

    # Step 9: Test Delete Many Operation
    ids_to_delete = [item.id for item in new_items]
    client.delete_many(ids_to_delete)
    print(f"Delete many successful: Deleted items with IDs {ids_to_delete}")

if __name__ == "__main__":
    test_client_endpoints()
