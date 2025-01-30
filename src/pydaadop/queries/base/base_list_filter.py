from typing import List, Optional

from bson import ObjectId


class BaseListFilter:
    def __init__(self, value: Optional[List[str]], key: str = "_id"):
        self.key = key
        self.value = value


    def to_mongo_filter(self):
        return {self.key: {"$in": [ObjectId(value) for value in self.value]}}


