"""
Unit tests for BaseMongoModel.
"""
from typing import Optional

import pytest
from bson import ObjectId

from pydaadop.models.base.base_mongo_model import BaseMongoModel


class SampleModel(BaseMongoModel):
    name: str
    age: int

    @staticmethod
    def create_index():
        return ["name"]


def test_default_id_is_generated():
    m = SampleModel(name="Alice", age=30)
    assert m.id is not None
    assert isinstance(m.id, str)
    # Should be a valid ObjectId string
    ObjectId(m.id)


def test_id_can_be_set_via_alias():
    oid = str(ObjectId())
    m = SampleModel(**{"_id": oid, "name": "Bob", "age": 25})
    assert m.id == oid


def test_id_can_be_set_via_field_name():
    oid = str(ObjectId())
    m = SampleModel(id=oid, name="Carol", age=20)
    assert m.id == oid


def test_model_dump_contains_id_as_underscore_id():
    m = SampleModel(name="Dave", age=40)
    data = m.model_dump()
    assert "_id" in data
    assert "id" not in data
    assert data["_id"] == m.id


def test_model_dump_exclude_id_via_ignore_id():
    m = SampleModel(name="Eve", age=35)
    data = m.model_dump(ignore_id=True)
    assert "_id" not in data
    assert "id" not in data


def test_model_dump_with_none_id():
    m = SampleModel(name="Frank", age=50)
    m.id = None  # type: ignore[assignment]
    data = m.model_dump()
    assert "_id" not in data
    assert "id" not in data


def test_model_dump_keys_returns_index_fields():
    m = SampleModel(name="Grace", age=28)
    keys = m.model_dump_keys()
    assert "name" in keys
    assert keys["name"] == "Grace"


def test_model_dump_keys_maps_id_to_underscore_id():
    class ModelWithIdIndex(BaseMongoModel):
        value: str

        @staticmethod
        def create_index():
            return ["id"]

    m = ModelWithIdIndex(value="test")
    keys = m.model_dump_keys()
    # "id" in create_index() → should be mapped to "_id" in the result
    assert "_id" in keys


def test_create_index_default_returns_id():
    m = BaseMongoModel()
    assert BaseMongoModel.create_index() == ["id"]


def test_two_instances_have_different_ids():
    m1 = BaseMongoModel()
    m2 = BaseMongoModel()
    assert m1.id != m2.id


def test_model_config_allows_population_by_name():
    oid = str(ObjectId())
    m = SampleModel(id=oid, name="Helen", age=22)
    assert m.id == oid
