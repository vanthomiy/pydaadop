from datetime import datetime

from pydaadop.models.base import BaseMongoModel
from my_definition import MyDefinition

class GenericModel(BaseMongoModel):
    str_value: str = ""
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: MyDefinition = MyDefinition.A

