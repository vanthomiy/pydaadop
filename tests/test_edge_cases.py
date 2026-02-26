"""
Edge-case tests for invalid or unusual Pydantic model configurations
passed to BaseQuery helpers.
"""
from __future__ import annotations

from typing import Any, List, Optional

import pytest

from pydaadop.models.base.base_mongo_model import BaseMongoModel
from pydaadop.queries.base.base_query import BaseQuery


# ── Empty model ───────────────────────────────────────────────────────────────

class EmptyModel(BaseMongoModel):
    """A model with no extra fields besides the inherited id."""
    pass


def test_create_filter_empty_model():
    FilterModel = BaseQuery.create_filter([EmptyModel], only_selectable=True)
    instance = FilterModel()
    result = BaseQuery.extract_filter(instance)
    assert result == {}


def test_create_sort_empty_model_returns_base_sort():
    from pydaadop.queries.base.base_sort import BaseSort
    SortModel = BaseQuery.create_sort([EmptyModel])
    # Should return BaseSort (or a subclass) without error
    instance = SortModel()
    assert hasattr(instance, "sort_by")


def test_create_range_empty_model():
    RangeModel = BaseQuery.create_range([EmptyModel])
    instance = RangeModel()
    assert hasattr(instance, "range_by")


def test_create_select_empty_model():
    SelectModel = BaseQuery.create_select([EmptyModel])
    instance = SelectModel()
    assert hasattr(instance, "selected_field")


# ── Model with only unsupported field types ───────────────────────────────────

class ListFieldModel(BaseMongoModel):
    """Model with a list field — not directly supported by _get_type."""
    tags: Optional[List[str]] = None


def test_create_filter_list_field_ignored():
    FilterModel = BaseQuery.create_filter([ListFieldModel], only_selectable=False)
    instance = FilterModel()
    result = BaseQuery.extract_filter(instance)
    # tags should not be in the filter (unsupported complex type)
    assert "tags" not in result


# ── split_filter ──────────────────────────────────────────────────────────────

class ModelA(BaseMongoModel):
    foo: str
    bar: int


class ModelB(BaseMongoModel):
    baz: float


def test_split_filter_assigns_to_correct_model():
    filter_data = {"foo": "hello", "baz": 3.14}
    split = BaseQuery.split_filter([ModelA, ModelB], filter_data)
    assert split[0] == {"foo": "hello"}
    assert split[1] == {"baz": 3.14}


def test_split_filter_unknown_key_is_dropped():
    filter_data = {"unknown_key": "value"}
    split = BaseQuery.split_filter([ModelA, ModelB], filter_data)
    assert split[0] == {}
    assert split[1] == {}


def test_split_filter_empty_data():
    split = BaseQuery.split_filter([ModelA, ModelB], {})
    assert split == [{}, {}]


# ── extract_range ─────────────────────────────────────────────────────────────

def test_extract_range_empty():
    from pydaadop.queries.base.base_range import BaseRange
    r = BaseRange()
    result = BaseQuery.extract_range(r)
    assert result == {}


def test_extract_range_gte_only():
    from pydaadop.queries.base.base_range import BaseRange
    r = BaseRange(range_by="price", gte_value="10")
    result = BaseQuery.extract_range(r)
    assert result == {"price": {"$gte": 10}}


def test_extract_range_lte_only():
    from pydaadop.queries.base.base_range import BaseRange
    r = BaseRange(range_by="price", lte_value="100")
    result = BaseQuery.extract_range(r)
    assert result == {"price": {"$lte": 100}}


def test_extract_range_both():
    from pydaadop.queries.base.base_range import BaseRange
    r = BaseRange(range_by="price", gte_value="5", lte_value="50")
    result = BaseQuery.extract_range(r)
    assert result == {"price": {"$gte": 5, "$lte": 50}}


def test_extract_range_non_digit_value():
    from pydaadop.queries.base.base_range import BaseRange
    r = BaseRange(range_by="name", gte_value="abc")
    result = BaseQuery.extract_range(r)
    assert result == {"name": {"$gte": "abc"}}


# ── extract_search ────────────────────────────────────────────────────────────

def test_extract_search_empty_search_term():
    from pydaadop.queries.base.base_search import BaseSearch
    result = BaseQuery.extract_search(ModelA, BaseSearch(search=""))
    assert result == {}


def test_extract_search_with_term():
    from pydaadop.queries.base.base_search import BaseSearch
    result = BaseQuery.extract_search(ModelA, BaseSearch(search="hello"))
    assert "$or" in result
    # Each clause should be a regex filter on a field
    or_clauses = result["$or"]
    assert len(or_clauses) > 0
    # All clauses should have $regex
    for clause in or_clauses:
        field = list(clause.keys())[0]
        assert "$regex" in clause[field]
        assert clause[field]["$regex"] == "hello"


# ── env_manager ───────────────────────────────────────────────────────────────

def test_get_mongo_uri_from_connection_string(monkeypatch):
    from pydaadop.utils.environment.env_manager import get_mongo_uri
    monkeypatch.setenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017")
    monkeypatch.delenv("MONGODB_USER", raising=False)
    result = get_mongo_uri()
    assert result == "mongodb://localhost:27017"


def test_get_mongo_uri_from_components(monkeypatch):
    from pydaadop.utils.environment.env_manager import get_mongo_uri
    monkeypatch.delenv("MONGO_CONNECTION_STRING", raising=False)
    monkeypatch.setenv("MONGODB_USER", "user")
    monkeypatch.setenv("MONGODB_PASS", "pass")
    monkeypatch.setenv("MONGO_BASE_URL", "localhost")
    monkeypatch.setenv("MONGO_PORT", "27017")
    result = get_mongo_uri()
    assert result == "mongodb://user:pass@localhost:27017"


def test_get_mongo_uri_missing_vars_raises(monkeypatch):
    from pydaadop.utils.environment.env_manager import get_mongo_uri
    monkeypatch.delenv("MONGO_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("MONGODB_USER", raising=False)
    monkeypatch.delenv("MONGODB_PASS", raising=False)
    monkeypatch.delenv("MONGO_BASE_URL", raising=False)
    monkeypatch.delenv("MONGO_PORT", raising=False)
    with pytest.raises(ValueError, match="Missing required environment variables"):
        get_mongo_uri()
