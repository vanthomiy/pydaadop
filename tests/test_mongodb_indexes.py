import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from pydaadop.database.no_sql.mongodb import BaseMongoDatabase


class DummyModel:
    @staticmethod
    def create_index():
        return ["name", "id"]


@pytest.mark.asyncio
async def test_ensure_indexes_schedules_or_runs(monkeypatch):
    # Create a fake collection with create_index as an AsyncMock
    fake_collection = MagicMock()
    fake_collection.create_index = AsyncMock(return_value="index_name")

    # Instantiate database with the fake collection
    db = BaseMongoDatabase(DummyModel, collection=fake_collection)

    # ensure_indexes should have attempted to call create_index at least once
    assert fake_collection.create_index.called
