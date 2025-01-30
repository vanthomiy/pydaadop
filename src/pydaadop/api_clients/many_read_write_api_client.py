from .read_write_api_client import ReadWriteApiClient
from typing import List, Dict, TypeVar
from ..models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class ManyReadWriteApiClient(ReadWriteApiClient[T]):
    def insert_many(self, items: List[T]) -> Dict:
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-insert-many"
        dict_items = [item.model_dump() for item in items]  # Convert each `Candle` to a JSON-serializable dictionary
        response_data = self._request("POST", endpoint, json=dict_items)
        return response_data

    def update_many(self, items: List[T]) -> Dict:
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-update-many"
        items_dict = [item.model_dump() for item in items]
        response_data = self._request("PUT", endpoint, json=items_dict)
        return response_data

    def update_field_many(self, items: List[dict], data: dict) -> Dict:
        if not items or len(items) == 0:
            return {}
        endpoint = self.model_class.__name__.lower() + "-update-field-many"
        data_dict = {"data": data}
        items_dict = [item for item in items]
        combined = {**data_dict, **items_dict}
        response_data = self._request("PUT", endpoint, json=combined)
        return response_data

    def delete_many(self, items: List[dict]) -> None:
        if not items or len(items) == 0:
            return
        # remove all empty dicts
        items = [item for item in items if item != {}]
        if not items or len(items) == 0:
            return
        endpoint = self.model_class.__name__.lower() + "-delete-many"
        self._request("DELETE", endpoint, json=items)