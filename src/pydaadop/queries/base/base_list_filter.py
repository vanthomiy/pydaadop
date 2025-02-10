from typing import List, Optional

from bson import ObjectId

class BaseListFilter:
    """
    BaseListFilter class for filtering lists of items by a specific key.

    Attributes:
        value (Optional[List[str]]): The list of values to filter by.
        key (str): The key to filter by (default is "_id").
    """
    def __init__(self, value: Optional[List[str]], key: str = "_id"):
        self.key = key
        self.value = value

    def to_mongo_filter(self):
        """
        Convert the filter to a MongoDB filter.

        Returns:
            dict: The MongoDB filter.
        """
        return {self.key: {"$in": [ObjectId(value) for value in self.value]}}


