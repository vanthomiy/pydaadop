from typing import List

from generic_model import GenericModel

class CustomModel(GenericModel):
    pass

    @staticmethod
    def create_index() -> List[str]:
        """
        We define that we want to create an index on the "test_enum" and "date_value" fields.
        Those combinations of fields will be unique in the collection and they are default for queries.
        """
        return ["test_enum", "date_value"]
