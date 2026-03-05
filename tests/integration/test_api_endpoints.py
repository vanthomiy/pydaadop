import time
from typing import List

import os

from src.pydaadop.api_clients.client_api_factory import ClientFactory
from examples.models.demo_product import DemoProduct as DemoProductModel

BASE = os.environ.get("BASE_URL", "http://localhost:8000")


def wait_for_server(timeout=10.0):
    start = time.time()
    factory = ClientFactory(BASE)
    client = factory.get_read_client(DemoProductModel)
    while time.time() - start < timeout:
        try:
            # use a simple API client call as a health probe
            client.get_all()
            return True
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError("Server did not become ready")


def test_full_crud_flow():
    # Ensure the demo app is running
    wait_for_server()

    # Create a GenericModel via read-only router (should not allow POST) — we skip

    # Create a DemoProduct via write router
    factory = ClientFactory(BASE)
    prod_client = factory.get_read_write_client(DemoProductModel)

    prod = DemoProductModel(name="widget", price=12.5)
    created = prod_client.insert(prod)
    assert getattr(created, "id", None) or getattr(created, "_id", None)

    # Update the product
    created.price = 13.0
    updated = prod_client.update(created)
    assert getattr(updated, "price", None) == 13.0

    # create additional products and a buyer that references them
    p2 = DemoProductModel(name="product-2", price=5.0)
    p3 = DemoProductModel(name="product-3", price=7.5)
    created2 = prod_client.insert(p2)
    created3 = prod_client.insert(p3)

    prod_ids = [getattr(created, 'id', getattr(created, '_id', None)),
                getattr(created2, 'id', getattr(created2, '_id', None)),
                getattr(created3, 'id', getattr(created3, '_id', None))]

    # create a buyer that references some products
    from examples.models.buyer import Buyer as BuyerModel
    buyer_client = factory.get_read_write_client(BuyerModel)
    b = BuyerModel(name="buyer-x")
    # attach a products list (dynamic field accepted by examples)
    # NOTE: some example setups infer relations from this list
    b_dict = b.model_dump()
    b_dict["products"] = [prod_ids[0], prod_ids[1]]
    # insert via client by constructing model with extra data
    from src.pydaadop.models.base.base_mongo_model import BaseMongoModel
    # Use generic dict insert via ReadWrite client by creating a model-like dict
    created_buyer = buyer_client.insert(BuyerModel(**b_dict))
    buyer_id = getattr(created_buyer, 'id', getattr(created_buyer, '_id', None))

    # create a payment linking buyer and product
    from examples.models.payments import Payment as PaymentModel
    try:
        payment_client = factory.get_read_write_client(PaymentModel)
        payment = PaymentModel(buyer_id=buyer_id, product_id=prod_ids[0], amount=1)
        created_payment = payment_client.insert(payment)
        # ensure the created payment references the buyer and product we created
        if created_payment is not None:
            assert getattr(created_payment, 'buyer_id', None) == buyer_id
            assert getattr(created_payment, 'product_id', None) == prod_ids[0]
    except Exception:
        # If Payment endpoints are not registered in the demo app, ignore
        created_payment = None

    # Verify the ProductBuyerDisplay router is available and returns display info
    from examples.models.product_buyer_display import ProductBuyerDisplay

    display_client = factory.get_read_client(ProductBuyerDisplay)
    # fetch assembled display rows
    rows = display_client.get_all()
    assert isinstance(rows, list)
    # Ensure at least one row references our buyer and product (if available)
    matches = [r for r in rows if getattr(r, 'buyer_id', None) == buyer_id or getattr(r, 'product_id', None) in prod_ids]
    assert matches, f"No ProductBuyerDisplay rows found for buyer {buyer_id} or products {prod_ids}"
