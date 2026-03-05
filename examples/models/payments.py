from src.pydaadop.models.base.base_mongo_model import BaseMongoModel


class Payment(BaseMongoModel):
    buyer_id: str
    product_id: str
    amount: int