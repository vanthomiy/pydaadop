from pydaadop.models.base.base_mongo_model import BaseMongoModel


class DemoProduct(BaseMongoModel):
    name: str
    price: float

    @staticmethod
    def create_index():
        return ["name"]
