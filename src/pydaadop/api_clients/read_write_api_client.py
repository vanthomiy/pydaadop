from .read_api_client import ReadApiClient
from typing import TypeVar, Type, Dict, Optional, Any

from ..models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class ReadWriteApiClient(ReadApiClient[T]):
    def insert(self, item: T) -> T:
        endpoint = self.model_class.__name__.lower()
        item_dict = item.model_dump()
        response_data = self._request("POST", endpoint, json=item_dict)
        return self.model_class(**response_data)

    def update(self, item: T) -> T:
        endpoint = f"{self.model_class.__name__.lower()}"
        item_dict = item.model_dump()
        response_data = self._request("PUT", endpoint, json=item_dict)
        return self.model_class(**response_data)

    def delete(self, key_filter_query: Optional[Dict[str, Any]]) -> None:
        _params = self._parse_query(key_filter_query=key_filter_query)
        endpoint = f"{self.model_class.__name__.lower()}"
        self._request("DELETE", endpoint, params=_params)