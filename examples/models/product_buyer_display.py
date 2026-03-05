from typing import Optional

from src.pydaadop.models.base.base_mongo_model import BaseMongoModel


class ProductBuyerDisplay(BaseMongoModel):
    product_id: str
    buyer_id: str
    product_name: str
    buyer_name: str
    amount: Optional[int]


    @staticmethod
    def create_index():
        return ["product_id", "buyer_id"]
