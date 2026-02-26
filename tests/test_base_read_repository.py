import pytest

from typing import List, Dict

from pydaadop.repositories.base.base_read_repository import BaseReadRepository
from pydaadop.models.base.base_mongo_model import BaseMongoModel
from pydaadop.models.display.display_item_info import DisplayItemInfo


class FakeCursor:
    def __init__(self, items: List[Dict]):
        self._items = items

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return self._items


class FakeCollection:
    def __init__(self, items=None, count=0):
        self._items = items or []
        self._count = count

    def find(self, *args, **kwargs):
        return FakeCursor(self._items)

    async def count_documents(self, filter_query=None):
        return self._count


@pytest.mark.asyncio
async def test_list_keys_returns_documents():
    items = [{"_id": "a"}, {"_id": "b"}]
    fake_collection = FakeCollection(items=items)
    repo = BaseReadRepository(BaseMongoModel, collection=fake_collection)
    result = await repo.list_keys(keys=["_id"], filter_query={})
    assert isinstance(result, list)
    assert result == items


@pytest.mark.asyncio
async def test_info_returns_display_item_info():
    fake_collection = FakeCollection(items=[], count=5)
    repo = BaseReadRepository(BaseMongoModel, collection=fake_collection)
    info = await repo.info(filter_query={}, search_query=None)
    assert isinstance(info, DisplayItemInfo)
    assert info.items_count == 5
