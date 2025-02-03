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
    """
    A base client for performing API operations on a specific model.

    Args:
        base_url (str): The base URL for the API.
        model_class (Type[T]): The model class to be used.
        headers (Dict[str, str], optional): Additional headers for the requests.
    """

    def __init__(self, base_url: str, model_class: Type[T], headers: Dict[str, str] = None):
        self.base_url = base_url
        self.model_class = model_class
        self.headers = headers or {}

    def _request(self, method: str, endpoint: str, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Sends a request to the API.

        Args:
            method (str): The HTTP method to use.
            endpoint (str): The API endpoint.
            **kwargs: Additional arguments for the request.

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: The response data from the API.

        Example:
            response = self._request("GET", "my_model")
        """
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
        """
        Parses various query parameters into a dictionary.

        Args:
            select_query (Optional[BaseSelect]): The select query parameters.
            paging_query (Optional[BasePaging]): The paging query parameters.
            filter_query (Optional[Dict[str, Any]]): The filter query parameters.
            sort_query (Optional[BaseSort]): The sort query parameters.
            search_query (Optional[Dict[str, Any]]): The search query parameters.
            range_query (Optional[BaseRange]): The range query parameters.
            key_filter_query (Optional[Dict[str, Any]]): The key filter query parameters.
            list_filter (Optional[BaseListFilter]): The list filter query parameters.

        Returns:
            dict[str, Any]: The parsed query parameters.

        Example:
            params = self.parse_query(filter_query={"name": "example"})
        """
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

        _params = {k: v for k, v in _params.items() if v is not None}

        return _params

    def get_query_info(self) -> Dict[str, Any]:
        """
        Retrieves query information for the model.

        Returns:
            Dict[str, Any]: The query information.

        Example:
            query_info = self.get_query_info()
        """
        return self._request("GET", f"{self.model_class.__name__.lower()}/display-info/query")

    def get_display_info(self, filter_query: Optional[Dict[str, Any]] = None, search_query: Optional[Dict[str, Any]] = None, range_query: Optional[BaseRange] = None) -> Dict[str, Any]:
        """
        Retrieves display information for the model.

        Args:
            filter_query (Optional[Dict[str, Any]]): The filter query parameters.
            search_query (Optional[Dict[str, Any]]): The search query parameters.
            range_query (Optional[BaseRange]): The range query parameters.

        Returns:
            Dict[str, Any]: The display information.

        Example:
            display_info = self.get_display_info(filter_query={"name": "example"})
        """
        _params = self.parse_query(None, None, filter_query, None, search_query, range_query)
        return self._request("GET", f"{self.model_class.__name__.lower()}/display-info/item", params=_params)

    def get_all(self,
                paging_query: Optional[BasePaging] = None,
                filter_query: Optional[Dict[str, Any]] = None,
                sort_query: Optional[BaseSort] = None,
                search_query: Optional[Dict[str, Any]] = None,
                range_query: Optional[BaseRange] = None,
                list_filter: Optional[BaseListFilter] = None) -> List[T]:
        """
        Retrieves all items of the model.

        Args:
            paging_query (Optional[BasePaging]): The paging query parameters.
            filter_query (Optional[Dict[str, Any]]): The filter query parameters.
            sort_query (Optional[BaseSort]): The sort query parameters.
            search_query (Optional[Dict[str, Any]]): The search query parameters.
            range_query (Optional[BaseRange]): The range query parameters.
            list_filter (Optional[BaseListFilter]): The list filter query parameters.

        Returns:
            List[T]: The list of items.

        Example:
            items = self.get_all(filter_query={"name": "example"})
        """
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
        """
        Retrieves all items of the model with selected fields.

        Args:
            select_query (Optional[BaseSelect]): The select query parameters.
            paging_query (Optional[BasePaging]): The paging query parameters.
            filter_query (Optional[Dict[str, Any]]): The filter query parameters.
            sort_query (Optional[BaseSort]): The sort query parameters.
            search_query (Optional[Dict[str, Any]]): The search query parameters.
            range_query (Optional[BaseRange]): The range query parameters.
            list_filter (Optional[BaseListFilter]): The list filter query parameters.

        Returns:
            List[Dict]: The list of items with selected fields.

        Example:
            items = self.get_all_select(select_query=BaseSelect(fields=["name"]))
        """
        _params = self.parse_query(select_query, paging_query, filter_query, sort_query, search_query, range_query, list_filter)

        data = self._request("GET", f"{self.model_class.__name__.lower()}/select", params=_params)
        return data

    def exists(self, key_filter_query: Optional[Dict[str, Any]]) -> bool:
        """
        Checks if an item exists in the database.

        Args:
            key_filter_query (Optional[Dict[str, Any]]): The key filter query parameters.

        Returns:
            bool: True if the item exists, False otherwise.

        Example:
            exists = self.exists(key_filter_query={"id": "example_id"})
        """
        _params = self.parse_query(key_filter_query=key_filter_query)
        data = self._request("GET", f"{self.model_class.__name__.lower()}/exists", params=_params)
        return bool(**data)

    def get(self, key_filter_query: Optional[Dict[str, Any]]) -> T:
        """
        Retrieves a single item from the database.

        Args:
            key_filter_query (Optional[Dict[str, Any]]): The key filter query parameters.

        Returns:
            T: The retrieved item.

        Example:
            item = self.get(key_filter_query={"id": "example_id"})
        """
        _params = self.parse_query(key_filter_query=key_filter_query)
        data = self._request("GET", f"{self.model_class.__name__.lower()}/item", params=_params)
        return self.model_class(**data)