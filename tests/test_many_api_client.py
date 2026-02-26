from pydaadop.api_clients.many_read_write_api_client import ManyReadWriteApiClient
from types import SimpleNamespace


class DummyModel:
    def __init__(self, name):
        self.name = name
        self.id = None

    def model_dump(self):
        return {"name": self.name}


def test_insert_many_maps_ids(monkeypatch):
    items = [DummyModel("a"), DummyModel("b")]

    def fake_request(method, endpoint, json=None):
        # simulate server returning dict with 'ids'
        return {"ids": ["id1", "id2"]}

    client = ManyReadWriteApiClient(base_url="http://x", model_class=DummyModel)
    monkeypatch.setattr(client, "_request", fake_request)

    resp = client.insert_many(items)
    assert resp.get("ids") == ["id1", "id2"]
    assert items[0].id == "id1"
    assert items[1].id == "id2"
