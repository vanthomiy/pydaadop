from typing import Literal, Optional
from enum import Enum

from pydaadop.queries.base.base_query import BaseQuery


def test_get_type_literal():
    t, selectable = BaseQuery._get_type(Literal["x", "y"])  # noqa: E501
    assert t is str
    assert selectable is True


def test_get_type_enum_optional():
    class E(Enum):
        A = "a"

    t, selectable = BaseQuery._get_type(Optional[E])
    assert t is str
    assert selectable is True
