"""
This module provides the BaseReadService class, which implements the ReadServiceInterface
for reading operations on MongoDB models.

Classes:
    BaseReadService: A base service class for reading operations on MongoDB models.
"""

from abc import ABC
from typing import TypeVar, List, Optional, Dict, Type

from fastapi import HTTPException
from pydantic import BaseModel
from typing_extensions import override

from ..interface.read_write_service_interface import ReadServiceInterface
from ...models.base import BaseMongoModel
from ...models.display import DisplayQueryInfo, DisplayItemInfo
from ...queries.base.base_list_filter import BaseListFilter
from ...queries.base.base_paging import BasePaging
from ...queries.base.base_query import BaseQuery
from ...queries.base.base_range import BaseRange
from ...queries.base.base_select import BaseSelect
from ...queries.base.base_sort import BaseSort
from ...repositories.base.base_read_repository import BaseReadRepository

S = TypeVar('S', bound=BaseMongoModel)
R = TypeVar('R', bound=BaseReadRepository[BaseMongoModel])

class BaseReadService(ReadServiceInterface[S], ABC):
    """
    A base service class for reading operations on MongoDB models.

    Attributes:
        repository (BaseReadRepository): The repository for reading operations.
    """

    def __init__(self, model: Type[S], repository: R = None):
        """
        Initialize the BaseReadService.

        Args:
            model (Type[S]): The MongoDB model type.
            repository (R, optional): The repository for reading operations. Defaults to None.
        """
        self.repository = repository if repository else BaseReadRepository(model)
        super().__init__(model)

    @override
    def create_filter(self) -> Type[BaseModel]:
        """
        Create a filter model for querying.

        Returns:
            Type[BaseModel]: The filter model.
        """
        return BaseQuery.create_filter(models=[self.model], only_selectable=True)

    @override
    def create_key_filter(self) -> Type[BaseModel]:
        """
        Create a key filter model for querying.

        Returns:
            Type[BaseModel]: The key filter model.
        """
        return BaseQuery.create_key_filter(models=[self.model])

    @override
    def create_sort(self) -> Type[BaseSort]:
        """
        Create a sort model for querying.

        Returns:
            Type[BaseSort]: The sort model.
        """
        return BaseQuery.create_sort(models=[self.model])

    @override
    def create_range(self) -> Type[BaseRange]:
        """
        Create a range model for querying.

        Returns:
            Type[BaseRange]: The range model.
        """
        return BaseQuery.create_range(models=[self.model])

    @override
    def create_select(self) -> Type[BaseSelect]:
        """
        Create a select model for querying.

        Returns:
            Type[BaseSelect]: The select model.
        """
        return BaseQuery.create_select(models=[self.model])

    @override
    async def exists(self, keys_filter_query: dict) -> bool:
        """
        Check if an item exists based on the filter query.

        Args:
            keys_filter_query (dict): The filter query.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        return await self.repository.exists(keys_filter_query)

    @override
    async def get(self, keys_filter_query: dict) -> S:
        """
        Get an item based on the filter query.

        Args:
            keys_filter_query (dict): The filter query.

        Returns:
            S: The retrieved item.

        Raises:
            HTTPException: If the item is not found.
        """
        item = await self.repository.get_by_id(keys_filter_query)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found.")
        return item

    @override
    async def list(self,
                   paging_query: BasePaging = BasePaging(),
                   filter_query: Dict = None,
                   sort_query: Optional[BaseSort] = None,
                   search_query: Dict = None,
                   range_query: Dict = None,
                   list_filter: BaseListFilter = None) -> List[S]:
        """
        List items based on various queries.

        Args:
            paging_query (BasePaging, optional): The paging query. Defaults to BasePaging().
            filter_query (Dict, optional): The filter query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): The list filter. Defaults to None.

        Returns:
            List[S]: The list of items.
        """
        filter_query = self._update_filter_query(filter_query, list_filter)
        if range_query:
            filter_query.update(range_query)
        return await self.repository.list(paging_query, filter_query, sort_query, search_query)

    @override
    async def list_keys(self,
                        keys: List[str],
                        filter_query: Dict = None,
                        search_query: Dict = None,
                        sort_query: Optional[BaseSort] = None,
                        range_query: Dict = None,
                        list_filter: BaseListFilter = None) -> List[Dict]:
        """
        List keys of items based on various queries.

        Args:
            keys (List[str]): The list of keys to retrieve.
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): The list filter. Defaults to None.

        Returns:
            List[Dict]: The list of keys.
        """
        filter_query = self._update_filter_query(filter_query, list_filter)
        if range_query:
            filter_query.update(range_query)
        return await self.repository.list_keys(keys=keys, filter_query=filter_query, search_query=search_query, sort_query=sort_query)

    @override
    async def item_info(self,
                        filter_query: Dict = None,
                        search_query: Dict = None,
                        range_query: Dict = None,
                        list_filter: BaseListFilter = None) -> DisplayItemInfo:
        """
        Get item information based on various queries.

        Args:
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            range_query (Dict, optional): The range query. Defaults to None.
            list_filter (BaseListFilter, optional): The list filter. Defaults to None.

        Returns:
            DisplayItemInfo: The item information.
        """
        updated_filter_query = self._update_filter_query(filter_query, list_filter)
        if range_query:
            updated_filter_query.update(range_query)
        return await self.repository.info(updated_filter_query, search_query)

    @override
    async def query_info(self, model: Type[S]) -> DisplayQueryInfo:
        """
        Get query information for the model.

        Args:
            model (Type[S]): The MongoDB model type.

        Returns:
            DisplayQueryInfo: The query information.
        """
        return DisplayQueryInfo(
            filter_info=BaseQuery.create_display_filter_info(model),
            sort_info=BaseQuery.create_display_sort_info(model)
        )
