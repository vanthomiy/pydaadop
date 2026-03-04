import time
from typing import List

import os
import requests
from examples.models.demo_product import DemoProduct as DemoProductModel
from examples.models.buyer import Buyer as BuyerModel
from examples.models.product_category import ProductCategory as ProductCategoryModel
from examples.models.product_definition import ProductDefinition
from pydaadop.api_clients.client_api_factory import ClientFactory


BASE = os.environ.get("BASE_URL", "http://localhost:8000")


def wait_for_server(timeout=15.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE}/health")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Server did not become ready")


def test_insert_many_and_verify_relations():
    """Insert many demo products, buyers and categories directly into MongoDB
    then query the API to ensure relations (product lists) are preserved.
    """
    wait_for_server()

    # Create demo products via the official API client
    factory = ClientFactory(BASE)
    prod_client = factory.get_read_write_client(DemoProductModel)
    prod_hex: List[str] = []
    for i in range(6):
        m = DemoProductModel(name=f"product-{i}", price=float(10 + i))
        created = prod_client.insert(m)
        prod_hex.append(getattr(created, 'id', getattr(created, '_id', None)))

    # Also test bulk insert via ManyReadWriteApiClient
    many_prod_client = factory.get_many_read_write_client(DemoProductModel)
    many_items = [DemoProductModel(name=f"many-{i}", price=1.0 + i) for i in range(2)]
    resp = many_prod_client.insert_many(many_items)
    # Ensure ids were assigned onto objects by insert_many mapping
    many_ids = [getattr(it, 'id', getattr(it, '_id', None)) for it in many_items]
    assert any(many_ids)

    # Create buyers via API referencing product ids
    b1 = BuyerModel(name="buyer-a", products=[prod_hex[0], prod_hex[1], prod_hex[2]])
    b2 = BuyerModel(name="buyer-b", products=[prod_hex[2], prod_hex[3], prod_hex[4]])
    buyer_client = factory.get_read_write_client(BuyerModel)
    created_b1 = buyer_client.insert(b1)
    created_b2 = buyer_client.insert(b2)
    assert getattr(created_b1, 'id', None) or getattr(created_b1, '_id', None)

    # Create categories via API
    c1 = ProductCategoryModel(name="cat-a", info="alpha", products=[prod_hex[0], prod_hex[1]], definition=ProductDefinition.A)
    c2 = ProductCategoryModel(name="cat-b", info="beta", products=[prod_hex[2], prod_hex[3], prod_hex[4]], definition=ProductDefinition.B)
    cat_client = factory.get_read_write_client(ProductCategoryModel)
    created_c1 = cat_client.insert(c1)
    created_c2 = cat_client.insert(c2)
    assert getattr(created_c1, 'id', None) or getattr(created_c1, '_id', None)

    # Query via API and verify counts and relations
    api_products = prod_client.get_all()
    assert isinstance(api_products, list)
    assert len(api_products) >= 6

    r = requests.get(f"{BASE}/buyer/")
    assert r.status_code == 200
    api_buyers = r.json()
    assert any(b["name"] == "buyer-a" for b in api_buyers)
    # verify referenced product ids appear in the product collection
    for b in api_buyers:
        if b.get("name") == "buyer-a":
            assert set(b.get("products", [])) >= {prod_hex[0], prod_hex[1]}

    r = requests.get(f"{BASE}/productcategory/")
    assert r.status_code == 200
    api_cats = r.json()
    assert any(c["name"] == "cat-a" for c in api_cats)
    for c in api_cats:
        if c.get("name") == "cat-b":
            # ensure the stored products are the ones we inserted
            assert set(c.get("products", [])) >= {prod_hex[2], prod_hex[3]}

    # Delete a single product via read-write client
    to_delete = prod_hex[0]
    prod_client._request("DELETE", "demoproduct", params={"_id": to_delete})

    # Delete many via many_client
    # collect ids from many_items
    delete_list = [{"_id": i} for i in many_ids if i]
    many_prod_client.delete_many(delete_list)
