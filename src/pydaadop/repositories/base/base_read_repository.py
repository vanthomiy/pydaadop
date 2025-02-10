"""
This module provides the BaseReadRepository class, which implements the repository
for reading MongoDB models.

Classes:
    BaseReadRepository: A repository class for reading MongoDB models.
"""

from typing import Type, TypeVar, List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository
from ...models.base import BaseMongoModel
from ...models.display import DisplayItemInfo
from ...queries.base.base_sort import BaseSort
from ...queries.base.base_paging import BasePaging

T = TypeVar("T", bound=BaseMongoModel)

class BaseReadRepository(BaseRepository[T]):
    """
    A repository class for reading MongoDB models.

    Attributes:
        collection (AsyncIOMotorCollection): The MongoDB collection.
    """

    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        """
        Initialize the BaseReadRepository.

        Args:
            model (Type[T]): The MongoDB model type.
            collection (AsyncIOMotorCollection, optional): The MongoDB collection. Defaults to None.
        """
        super().__init__(model, collection)

    async def exists(self, keys_filter_query: dict) -> bool:
        """
        Check if an item exists based on the filter query.

        Args:
            keys_filter_query (dict): The filter query.

        Returns:
            bool: True if the item exists, False otherwise.
        """
        return await self.collection.count_documents(keys_filter_query) > 0

    async def get_by_id(self, keys_filter_query: dict) -> Optional[T]:
        """
        Get an item based on the filter query.

        Args:
            keys_filter_query (dict): The filter query.

        Returns:
            Optional[T]: The retrieved item, or None if not found.
        """
        data = await self.collection.find_one(keys_filter_query)
        return self.model(**data) if data else None

    async def list(
            self, paging_query: BasePaging = BasePaging(),
            filter_query: Dict = None,
            sort_query: Optional[BaseSort] = None,
            search_query: Dict = None
    ) -> List[T]:
        """
        List items based on various queries.

        Args:
            paging_query (BasePaging, optional): The paging query. Defaults to BasePaging().
            filter_query (Dict, optional): The filter query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.

        Returns:
            List[T]: The list of items.
        """
        if filter_query is None:
            filter_query = {}
        filter_query.update(search_query or {})

        cursor = self.collection.find(filter_query).skip(paging_query.skip()).limit(paging_query.limit())

        if sort_query and sort_query.sort_by and sort_query.sort_order:
            sort_order = 1 if sort_query.sort_order == "asc" else -1
            if sort_query.sort_by:
                cursor = cursor.sort(sort_query.sort_by, sort_order)

        items = [self.model(**item) async for item in cursor]
        return items

    async def list_keys(
            self, keys: List[str],
            filter_query: Dict = None,
            search_query: Dict = None,
            sort_query: Optional[BaseSort] = None,
    ) -> List[Dict]:
        """
        List keys of items based on various queries.

        Args:
            keys (List[str]): The list of keys to retrieve.
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.
            sort_query (Optional[BaseSort], optional): The sort query. Defaults to None.

        Returns:
            List[Dict]: The list of keys.
        """
        if filter_query is None:
            filter_query = {}
        filter_query.update(search_query or {})

        # Use self.collection to perform the query, projecting only the _id field
        cursor = self.collection.find(filter_query, {key: 1 for key in keys})

        if sort_query and sort_query.sort_by and sort_query.sort_order:
            sort_order = 1 if sort_query.sort_order == "asc" else -1
            if sort_query.sort_by:
                cursor = cursor.sort(sort_query.sort_by, sort_order)

        # Fetch the IDs asynchronously, this time we only request the _id field
        result_keys = await cursor.to_list(length=None)  # Fetch all matching documents

        # Directly extract the ID from the result
        return result_keys

    async def info(self, filter_query: Dict = None, search_query: Dict = None) -> DisplayItemInfo:
        """
        Get item information based on various queries.

        Args:
            filter_query (Dict, optional): The filter query. Defaults to None.
            search_query (Dict, optional): The search query. Defaults to None.

        Returns:
            DisplayItemInfo: The item information.
        """
        # get the count of the items
        if filter_query is None:
            filter_query = {}
        filter_query.update(search_query or {})

        count = await self.collection.count_documents(filter_query)
        return DisplayItemInfo(items_count=count)