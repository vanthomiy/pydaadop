from typing import Type, TypeVar, Generic, Dict, Any, List, Optional, Union

from fastapi import Depends

from ..queries.base.base_range import BaseRange
from requests import request, Response

from ..models.base import BaseMongoModel
from ..queries.base.base_list_filter import BaseListFilter
from ..queries.base.base_paging import BasePaging
from ..queries.base.base_select import BaseSelect
from ..queries.base.base_sort import BaseSort

T = TypeVar("T", bound=BaseMongoModel)

class BaseApiClient(Generic[T]):
    def __init__(self, base_url: str, model_class: Type[T], headers: Dict[str, str] = None):
        self.base_url = base_url
        self.model_class = model_class
        self.headers = headers or {}

    def _request(self, method: str, endpoint: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        url = f"{self.base_url}/{endpoint}/"
        response: Response = request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    @classmethod
    def parse_query(cls,
                select_query: Optional[BaseSelect] = None,
                paging_query: Optional[BasePaging] = None,
                filter_query: Optional[Dict[str, Any]] = None,
                sort_query: Optional[BaseSort] = None,
                search_query: Optional[Dict[str, Any]] = None,
                range_query: Optional[BaseRange] = None,
                key_filter_query: Optional[Dict[str, Any]] = None,
                list_filter: Optional[BaseListFilter] = None) -> dict[str, Any]:
        _params: Dict[str, Any] = {}

        if paging_query:
            _params.update(paging_query.model_dump())
        if filter_query:
            _params.update(filter_query)
        if key_filter_query:
            _params.update(key_filter_query)
        if search_query:
            _params.update(search_query)
        if list_filter:
            _params.update(list_filter.to_mongo_filter())
        if sort_query:
            _params.update(sort_query.model_dump())
        if select_query:
            _params.update(select_query.model_dump())
        if range_query:
            _params.update(range_query.model_dump())

        # Remove None values from the filter
        _params = {k: v for k, v in _params.items() if v is not None}

        return _params

    def get_display_into(self, filter_query: Optional[Dict[str, Any]] = None, search_query: Optional[Dict[str, Any]] = None, range_query: Optional[BaseRange] = None) -> Dict[str, Any]:
        _params = self.parse_query(None, None, filter_query, None, search_query, range_query)
        return self._request("GET", f"{self.model_class.__name__.lower()}/display-info/item", params=_params)

    def get_all(self,
                paging_query: Optional[BasePaging] = None,
                filter_query: Optional[Dict[str, Any]] = None,
                sort_query: Optional[BaseSort] = None,
                search_query: Optional[Dict[str, Any]] = None,
                range_query: Optional[BaseRange] = None,
                list_filter: Optional[BaseListFilter] = None) -> List[T]:

        _params = self.parse_query(None, paging_query, filter_query, sort_query, search_query, range_query, list_filter)

        data = self._request("GET", f"{self.model_class.__name__.lower()}", params=_params)
        return [self.model_class(**item) for item in data]

    def get_all_select(self,
                select_query: Optional[BaseSelect] = None,
                paging_query: Optional[BasePaging] = None,
                filter_query: Optional[Dict[str, Any]] = None,
                sort_query: Optional[BaseSort] = None,
                search_query: Optional[Dict[str, Any]] = None,
                range_query: Optional[BaseRange] = None,
                list_filter: Optional[BaseListFilter] = None) -> List[Dict]:
        _params = self.parse_query(select_query, paging_query, filter_query, sort_query, search_query, range_query, list_filter)

        data = self._request("GET", f"{self.model_class.__name__.lower()}/select", params=_params)
        return data

    def exists(self, key_filter_query: Optional[Dict[str, Any]]) -> bool:
        _params = self.parse_query(key_filter_query=key_filter_query)
        data = self._request("GET", f"{self.model_class.__name__.lower()}/exists", params=_params)
        return bool(**data)

    def get(self, key_filter_query: Optional[Dict[str, Any]]) -> T:
        _params = self.parse_query(key_filter_query=key_filter_query)
        data = self._request("GET", f"{self.model_class.__name__.lower()}/item", params=_params)
        return self.model_class(**data)