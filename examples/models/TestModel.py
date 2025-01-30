from datetime import datetime
from enum import Enum
from typing import List

from src.deriven_core.models.base import BaseMongoModel

class TestEnum(str, Enum):
    A='allow'
    B='below'
    C='celow'


class TestModel(BaseMongoModel):
    str_value: float = 0
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: TestEnum = TestEnum.A

    @staticmethod
    def create_index() -> List[str]:
        return ["str_value", "int_value"]


class TestModel2(BaseMongoModel):
    str_value: float = 0
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: TestEnum = TestEnum.A
