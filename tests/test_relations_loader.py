import pytest
from bson import ObjectId

from pydaadop.relations.core import (
    Relation,
    normalize_id,
    get_relations_for_model,
    load_relations,
)
from pydaadop.models.base.base_mongo_model import BaseMongoModel


class Athlete(BaseMongoModel):
    id: ObjectId
    name: str


class Result(BaseMongoModel):
    id: ObjectId
    athlete_id: ObjectId
    # relation metadata defined via __fields__ extras would normally be set by Field(...),
    # but here we simulate it by constructing a Relation manually in tests.


class FakeRepo:
    def __init__(self, items):
        self.items = items

    async def get_many_by_ids(self, ids, projection=None):
        s = {str(i): i for i in self.items}
        return [s.get(str(i)) for i in ids if s.get(str(i))]


@pytest.mark.asyncio
async def test_normalize_id_and_load_relations():
    a1 = Athlete(id=ObjectId(), name="A1")
    a2 = Athlete(id=ObjectId(), name="A2")

    r1 = Result(id=ObjectId(), athlete_id=a1.id)
    r2 = Result(id=ObjectId(), athlete_id=str(a2.id))

    # patch get_relations_for_model to return a single relation definition
    rel = Relation(
        name="athlete", by="athlete_id", model=Athlete, repo_key="athlete", many=False
    )

    # create repos mapping
    repo = FakeRepo([a1, a2])

    # Monkeypatch get_relations_for_model to return our relation (simple approach)
    from pydaadop.relations import core

    original = core.get_relations_for_model

    def fake_get_relations_for_model(model):
        return {"athlete": rel}

    core.get_relations_for_model = fake_get_relations_for_model

    try:
        await load_relations([r1, r2], include=["athlete"], repos={"athlete": repo})
        assert hasattr(r1, "athlete")
        assert hasattr(r2, "athlete")
        assert r1.athlete.name == "A1"
        assert r2.athlete.name == "A2"
    finally:
        core.get_relations_for_model = original
