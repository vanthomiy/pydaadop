from fastapi.testclient import TestClient
from examples.demo.api import app
import json

client = TestClient(app)
resp = client.get("/productcategory/display-info/query/")
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))
