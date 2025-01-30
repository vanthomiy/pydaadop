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

    @abstractmethod
    async def exists(self, keys_filter_query: dict) -> bool:
        """Check if an item exists by its unique ID."""
        pass

    @abstractmethod
    async def get(self, keys_filter_query: dict) -> S:
        """Retrieve an item by its unique ID."""
        pass

    @abstractmethod
    async def list(self,
                   paging_query: BasePaging = BasePaging(),
                   filter_query: Dict = None,
                   sort_query: Optional[BaseSort] = None,
                   search_query: Dict = None,
                   range_query: Dict = None,
                   list_filter: BaseListFilter = None) -> List[S]:
        """List items with optional paging, filtering, sorting, and search queries."""
        pass

    @abstractmethod
    async def list_keys(self,
                    keys: List[str],
                    filter_query: Dict = None,
                    search_query: Dict = None,
                    sort_query: Optional[BaseSort] = None,
                    range_query: Dict = None,
                    list_filter: BaseListFilter = None) -> List[Dict]:
        """List items with optional filtering, search, and keys."""
        pass

    @abstractmethod
    async def item_info(self,
                        filter_query: Dict = None,
                        search_query: Dict = None,
                        range_query: Dict = None,
                        list_filter: BaseListFilter = None) -> DisplayItemInfo:
        """Retrieve information about items with optional filtering and search."""
        pass

    @abstractmethod
    async def query_info(self, model: Type[S]) -> DisplayQueryInfo:
        """Generate display query info for the provided model."""
        pass

