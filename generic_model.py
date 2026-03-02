from datetime import datetime

from pydaadop.models.base import BaseMongoModel
from .my_definition import MyDefinition


class GenericModel(BaseMongoModel):
    """A generic example model used by the examples suite.

    This model is intentionally simple and demonstrates a read-only API in
    the demo application.
    """

    str_value: str = ""
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: MyDefinition = MyDefinition.A

