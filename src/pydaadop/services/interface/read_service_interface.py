"""
This module provides the ReadServiceInterface class, which defines the interface for service classes
that handle read operations on a model.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Type, Any
from pydantic import BaseModel

from .service_interface import ServiceInterface
from ...models.display import DisplayQueryInfo, DisplayItemInfo
from ...queries.base.base_list_filter import BaseListFilter
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_sort import BaseSort

S = TypeVar('S', bound=BaseModel)

@abstractmethod
class ReadServiceInterface(ServiceInterface[S]):
    """
    Interface for service classes that handle read operations on a model.
    """

    @abstractmethod
    async def exists(self, keys_filter_query: dict) -> bool:
        """
        Check if an item exists by its unique ID.

        Args:
            keys_filter_query (dict): The filter query to identify the item.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        pass

    @abstractmethod
    async def get(self, keys_filter_query: dict) -> S:
        """
        Retrieve an item by its unique ID.

        Args:
            keys_filter_query (dict): The filter query to identify the item.

        Returns:
            S: The retrieved item.
        """
        pass

    @abstractmethod
    async def list(self,
                   paging_query: BasePaging = BasePaging(),
                   filter_query: Dict = None,
                   sort_query: Optional[BaseSort] = None,
                   search_query: Dict = None,
                   range_query: Dict = None,
                   list_filter: BaseListFilter = None) -> List[S]:
        """
        List items with optional paging, filtering, sorting, and search queries.

        Args:
            paging_query (BasePaging, optional): The paging query. Defaults to BasePaging().
            filter_query (Dict, optional): The filter query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): Additional filters. Defaults to None.

        Returns:
            List[S]: The list of items.
        """
        pass

    @abstractmethod
    async def list_keys(self,
                    keys: List[str],
                    filter_query: Dict = None,
                    search_query: Dict = None,
                    sort_query: Optional[BaseSort] = None,
                    range_query: Dict = None,
                    list_filter: BaseListFilter = None) -> List[Dict]:
        """
        List items with optional filtering, search, and keys.

        Args:
            keys (List[str]): The list of keys to retrieve.
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): Additional filters. Defaults to None.

        Returns:
            List[Dict]: The list of items.
        """
        pass

    @abstractmethod
    async def item_info(self,
                        filter_query: Dict = None,
                        search_query: Dict = None,
                        range_query: Dict = None,
                        list_filter: BaseListFilter = None) -> DisplayItemInfo:
        """
        Retrieve information about items with optional filtering and search.

        Args:
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): Additional filters. Defaults to None.

        Returns:
            DisplayItemInfo: The information about the items.
        """
        pass

    @abstractmethod
    async def query_info(self, model: Type[S]) -> DisplayQueryInfo:
        """
        Generate display query info for the provided model.

        Args:
            model (Type[S]): The model class.

        Returns:
            DisplayQueryInfo: The display query info.
        """
        pass

