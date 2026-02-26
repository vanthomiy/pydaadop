"""
Extended unit tests for BaseQuery.
"""
from enum import Enum
from typing import Literal, Optional

import pytest

from pydaadop.queries.base.base_query import BaseQuery
from pydaadop.queries.base.base_sort import BaseSort
from pydaadop.models.base.base_mongo_model import BaseMongoModel


# ── Models used across tests ──────────────────────────────────────────────────

class Color(Enum):
    RED = "red"
    BLUE = "blue"


class ItemModel(BaseMongoModel):
    name: str
    price: float
    quantity: int
    category: Optional[Literal["A", "B", "C"]] = None
    color: Optional[Color] = None
    active: Optional[bool] = None


class TagModel(BaseMongoModel):
    tag: str
    weight: int


# ── _get_type ─────────────────────────────────────────────────────────────────

def test_get_type_str():
    t, sel = BaseQuery._get_type(str)
    assert t is str
    assert sel is False


def test_get_type_int():
    t, sel = BaseQuery._get_type(int)
    assert t is int
    assert sel is False


def test_get_type_float():
    t, sel = BaseQuery._get_type(float)
    assert t is float
    assert sel is False


def test_get_type_optional_str():
    t, sel = BaseQuery._get_type(Optional[str])
    assert t is str
    assert sel is False


def test_get_type_literal_str():
    t, sel = BaseQuery._get_type(Literal["x", "y"])
    assert t is str
    assert sel is True


def test_get_type_literal_int():
    t, sel = BaseQuery._get_type(Literal[1, 2, 3])
    assert t is int
    assert sel is True


def test_get_type_enum():
    t, sel = BaseQuery._get_type(Color)
    assert t is str
    assert sel is True


def test_get_type_optional_enum():
    t, sel = BaseQuery._get_type(Optional[Color])
    assert t is str
    assert sel is True


def test_get_type_bool():
    # bool is not in supported_types [str, int, float]; _get_type returns (None, False)
    t, sel = BaseQuery._get_type(bool)
    assert t is None


def test_get_type_unknown():
    t, sel = BaseQuery._get_type(object)
    assert t is None


def test_get_type_none():
    t, sel = BaseQuery._get_type(None)
    assert t is None
    assert sel is False


# ── _get_allowed_values ───────────────────────────────────────────────────────

def test_get_allowed_values_literal():
    vals = BaseQuery._get_allowed_values(Literal["A", "B", "C"])
    assert vals == ["A", "B", "C"]


def test_get_allowed_values_optional_literal():
    vals = BaseQuery._get_allowed_values(Optional[Literal["x", "y"]])
    assert vals == ["x", "y"]


def test_get_allowed_values_plain_type():
    vals = BaseQuery._get_allowed_values(str)
    assert vals is None


# ── _is_supported_type ────────────────────────────────────────────────────────

def test_is_supported_type_not_only_selectable():
    assert BaseQuery._is_supported_type(str, False, "name", only_selectable=False) is True


def test_is_supported_type_id_field():
    assert BaseQuery._is_supported_type(str, False, "user_id", only_selectable=True) is True


def test_is_supported_type_selectable():
    assert BaseQuery._is_supported_type(str, True, "category", only_selectable=True) is True


def test_is_supported_type_bool_in_selectable_types():
    assert BaseQuery._is_supported_type(bool, False, "active", only_selectable=True) is True


def test_is_supported_type_plain_str_only_selectable_false():
    # str is not selectable and name doesn't end in _id
    assert BaseQuery._is_supported_type(str, False, "name", only_selectable=True) is False


# ── get_fields_of_model ───────────────────────────────────────────────────────

def test_get_fields_of_model_only_selectable():
    fields = BaseQuery.get_fields_of_model(ItemModel, only_selectable=True)
    # "category" (Literal) and "color" (Enum) are selectable
    assert "category" in fields
    assert "color" in fields
    # plain str/float/int are not selectable
    assert "name" not in fields
    assert "price" not in fields
    # Optional[bool] excluded: _get_type returns (None, False) since the unwrapped type
    # must be in supported_selectable_types but bool wraps to None via _get_type.
    assert "active" not in fields


def test_get_fields_of_model_all():
    fields = BaseQuery.get_fields_of_model(ItemModel, only_selectable=False)
    # All supported-type fields should be present
    assert "name" in fields
    assert "price" in fields
    assert "quantity" in fields
    assert "category" in fields


# ── create_filter ─────────────────────────────────────────────────────────────

def test_create_filter_returns_model_class():
    FilterModel = BaseQuery.create_filter([ItemModel], only_selectable=True)
    assert hasattr(FilterModel, "model_fields")


def test_create_filter_fields_are_optional():
    FilterModel = BaseQuery.create_filter([ItemModel], only_selectable=False)
    instance = FilterModel()
    # All fields should default to None
    for field in FilterModel.model_fields:
        assert getattr(instance, field) is None


# ── extract_filter ────────────────────────────────────────────────────────────

def test_extract_filter_excludes_none_by_default():
    FilterModel = BaseQuery.create_filter([ItemModel], only_selectable=False)
    instance = FilterModel()
    result = BaseQuery.extract_filter(instance)
    assert result == {}


def test_extract_filter_includes_set_values():
    FilterModel = BaseQuery.create_filter([ItemModel], only_selectable=False)
    instance = FilterModel(name="Widget")
    result = BaseQuery.extract_filter(instance)
    assert result == {"name": "Widget"}


def test_extract_filter_maps_id_to_underscore_id():
    FilterModel = BaseQuery.create_filter([BaseMongoModel], only_selectable=False)
    oid = "abc123"
    instance = FilterModel(id=oid)
    result = BaseQuery.extract_filter(instance)
    assert "_id" in result
    assert result["_id"] == oid


# ── split_sort ────────────────────────────────────────────────────────────────

def test_split_sort_no_sort_by():
    result = BaseQuery.split_sort([ItemModel, TagModel], BaseSort(sort_by=None))
    assert result == [None, None]


def test_split_sort_first_model():
    sort = BaseSort(sort_by="name", sort_order="asc")
    result = BaseQuery.split_sort([ItemModel, TagModel], sort)
    assert result[0] is not None
    assert result[0].sort_by == "name"
    assert result[1] is None


def test_split_sort_second_model():
    sort = BaseSort(sort_by="tag", sort_order="desc")
    result = BaseQuery.split_sort([ItemModel, TagModel], sort)
    assert result[0] is None
    assert result[1] is not None
    assert result[1].sort_by == "tag"


def test_split_sort_unknown_field_returns_none_list():
    sort = BaseSort(sort_by="nonexistent_field", sort_order="asc")
    result = BaseQuery.split_sort([ItemModel, TagModel], sort)
    assert result == [None, None]


# ── create_sort / create_range / create_select ────────────────────────────────

def test_create_sort_returns_sort_class():
    SortModel = BaseQuery.create_sort([ItemModel])
    instance = SortModel()
    assert hasattr(instance, "sort_by")
    assert hasattr(instance, "sort_order")


def test_create_range_returns_range_class():
    RangeModel = BaseQuery.create_range([ItemModel])
    instance = RangeModel()
    assert hasattr(instance, "range_by")


def test_create_select_returns_select_class():
    SelectModel = BaseQuery.create_select([ItemModel])
    instance = SelectModel()
    assert hasattr(instance, "selected_field")


# ── combine helpers ───────────────────────────────────────────────────────────

def test_combine_display_filter_info():
    info1 = BaseQuery.create_display_filter_info(ItemModel)
    info2 = BaseQuery.create_display_filter_info(TagModel)
    combined = BaseQuery.combine_display_filter_info([info1, info2])
    # ItemModel has selectable fields (Literal/Enum); TagModel has none (plain str/int)
    all_parents = {a.parent for a in combined.filter_attributes}
    assert "ItemModel" in all_parents
    # TagModel has no selectable filter fields, so it does not appear
    assert len(combined.filter_attributes) == len(info1.filter_attributes)


def test_combine_display_sort_info():
    info1 = BaseQuery.create_display_sort_info(ItemModel)
    info2 = BaseQuery.create_display_sort_info(TagModel)
    combined = BaseQuery.combine_display_sort_info([info1, info2])
    all_parents = {a.parent for a in combined.sort_attributes}
    assert "ItemModel" in all_parents
    assert "TagModel" in all_parents
