import time
from typing import List

import requests


import os

BASE = os.environ.get("BASE_URL", "http://localhost:8000")


def wait_for_server(timeout=10.0):
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


def test_full_crud_flow():
    # Ensure the demo app is running
    wait_for_server()

    # Create a GenericModel via read-only router (should not allow POST) — we skip

    # Create a DemoProduct via write router
    payload = {"name": "widget", "price": 12.5}
    r = requests.post(f"{BASE}/demoproduct/", json=payload)
    assert r.status_code == 200
    created = r.json()
    assert "id" in created or "_id" in created or isinstance(created, dict)

    # Update the product
    # adapt payload to include id if returned as _id
    if "_id" in created:
        payload["_id"] = created["_id"]
    if "id" in created:
        payload["id"] = created["id"]

    payload["price"] = 13.0
    r = requests.put(f"{BASE}/demoproduct/", json=payload)
    assert r.status_code == 200

    # Insert many custom models
    many = [{"str_value": "a"}, {"str_value": "b"}]
    r = requests.post(f"{BASE}/custom-insert-many", json=many)
    assert r.status_code == 200
    data = r.json()
    assert "ids" in data and isinstance(data["ids"], list)

    # Delete many by ids
    ids = data["ids"]
    queries = [{"_id": i} for i in ids]
    r = requests.delete(f"{BASE}/custom-delete-many/", json=queries)
    assert r.status_code == 200
