from typing import List, Optional

from pydantic import Field

from examples.models.demo_product import DemoProduct

from .generic_model import GenericModel


class CustomModel(GenericModel):
    """A small custom model used to demonstrate the "many" read-write router.

    This model stores a reference to a DemoProduct via `product_id` and declares
    a relation on `product` so the demo loader can attach the referenced
    DemoProduct instance when requested.
    """

    product_id: Optional[str] = None
    product: Optional[DemoProduct] = Field(
        default=None,
        relation={
            "by": "product_id",
            "model": DemoProduct,
            "repo": "demoproduct",
            "many": False,
            "include_by_default": False,
        },
    )

    info: str = ""
