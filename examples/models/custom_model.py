from typing import List

from examples.models.demo_product import DemoProduct

from .generic_model import GenericModel


class CustomModel(GenericModel):
    """A small custom model used to demonstrate the "many" read-write router."""
    product: DemoProduct

    @staticmethod
    def create_index() -> List[str]:
        """Create a compound index on `test_enum` and `date_value` for the example."""
        return ["test_enum", "date_value"]
