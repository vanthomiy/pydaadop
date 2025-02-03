from datetime import datetime

from src.deriven_core.models.base import BaseMongoModel
from examples.models.definitions import Definition1


class GenericModel(BaseMongoModel):
    str_value: float = 0
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: Definition1 = Definition1.A

