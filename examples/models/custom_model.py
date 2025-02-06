from datetime import datetime
from typing import List

from pydaadop.models.base import BaseMongoModel
from my_definition import MyDefinition


class CustomModel(BaseMongoModel):
    str_value: str = ""
    int_value: int = 0
    float_value: float = 0
    date_value: datetime = datetime.now()
    test_enum: MyDefinition = MyDefinition.A

    @staticmethod
    def create_index() -> List[str]:
        """
        We define that we want to create an index on the "test_enum" and "date_value" fields.
        Those combinations of fields will be unique in the collection and they are default for queries.
        """
        return ["test_enum", "date_value"]
