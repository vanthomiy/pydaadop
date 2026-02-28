import pytest
from bson import ObjectId

from pydaadop.relations.core import (
    Relation,
    register_repo,
    clear_repo_registry,
    load_relations,
)
from pydaadop.models.base.base_mongo_model import BaseMongoModel
from typing import Any


class Tag(BaseMongoModel):
    id: ObjectId
    name: str


class ResultWithTags(BaseMongoModel):
    id: ObjectId
    tag_ids: Any


class FakeTagRepo:
    def __init__(self, items):
        self.items = items

    async def get_many_by_ids(self, ids, projection=None):
        s = {
            str(getattr(item, "id", getattr(item, "_id", None))): item
            for item in self.items
        }
        # debug print for test investigation
        print("FakeTagRepo.get_many_by_ids called with ids:", [str(i) for i in ids])
        print("FakeTagRepo available keys:", list(s.keys()))
        result = []
        for i in ids:
            key = str(i)
            if key in s:
                result.append(s[key])
        return result


@pytest.mark.asyncio
async def test_register_repo_and_many_relation():
    t1 = Tag(id=ObjectId(), name="t1")
    t2 = Tag(id=ObjectId(), name="t2")

    r = ResultWithTags(id=ObjectId(), tag_ids=[t1.id, str(t2.id)])

    rel = Relation(name="tags", by="tag_ids", model=Tag, repo_key="tag", many=True)

    clear_repo_registry()
    fake_repo = FakeTagRepo([t1, t2])
    register_repo("tag", fake_repo)

    # Monkeypatch get_relations_for_model to return our relation
    from pydaadop.relations import core

    original = core.get_relations_for_model

    def fake_get_relations_for_model(model):
        return {"tags": rel}

    core.get_relations_for_model = fake_get_relations_for_model

    try:
        await load_relations([r], include=["tags"])
        assert hasattr(r, "tags")
        assert isinstance(r.tags, list)
        assert len(r.tags) == 2
    finally:
        core.get_relations_for_model = original
        clear_repo_registry()
