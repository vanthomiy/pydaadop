from typing import List, Optional

from pydantic import Field

from examples.models.demo_product import DemoProduct
from examples.models.product_definition import ProductDefinition
from pydaadop.models.base.base_mongo_model import BaseMongoModel


class ProductCategory(BaseMongoModel):
    name: str    
    info: str = ""
    products: Optional[List[str]] = Field(default_factory=list)
    definition: ProductDefinition 