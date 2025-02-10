"""
This module provides the ManyReadWriteService class, which implements the ManyReadWriteServiceInterface
and provides methods for creating, updating, and deleting multiple items in a MongoDB collection.
"""

from abc import ABC
from typing import TypeVar, Type, List
from pydantic import BaseModel
from pymongo.results import InsertManyResult, BulkWriteResult, DeleteResult
from typing_extensions import override

from ..base.base_read_write_service import BaseReadWriteService
from ..interface.many_read_write_service_interface import ManyReadWriteServiceInterface
from ...models.base import BaseMongoModel
from ...repositories.many.many_read_write_repository import ManyReadWriteRepository

S = TypeVar('S', bound=BaseMongoModel)
R = TypeVar('R', bound=ManyReadWriteRepository[BaseMongoModel])

class ManyReadWriteService(ManyReadWriteServiceInterface[S], BaseReadWriteService[S], ABC):
    """
    Service class for handling multiple read and write operations on a MongoDB collection.

    Attributes:
        model (Type[S]): The model class.
        repository (R): The repository instance for database operations.
    """

    def __init__(self, model: Type[S], repository: R = None):
        """
        Initialize the ManyReadWriteService.

        Args:
            model (Type[S]): The model class.
            repository (R, optional): The repository instance for database operations. Defaults to None.
        """
        self.repository = repository if repository else ManyReadWriteRepository(model)
        super().__init__(model, self.repository)

    @override
    async def create_many(self, items: List[S]) -> InsertManyResult:
        """
        Create multiple items in the collection.

        Args:
            items (List[S]): List of items to be created.

        Returns:
            InsertManyResult: The result of the insert operation.
        """
        return await self.repository.create_many(items)

    @override
    async def update_many(self, items: List[S]) -> BulkWriteResult:
        """
        Update multiple items in the collection.

        Args:
            items (List[S]): List of items to be updated.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        return await self.repository.update_many(items)

    @override
    async def update_field_many(self, key_filter_queries: List[dict], data: dict) -> BulkWriteResult:
        """
        Update specific fields of multiple items in the collection.

        Args:
            key_filter_queries (List[dict]): List of filter queries to identify items.
            data (dict): Data to be updated.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        return await self.repository.update_field_many(key_filter_queries, data)

    @override
    async def delete_many(self, key_filter_queries: List[dict]) -> DeleteResult:
        """
        Delete multiple items from the collection.

        Args:
            key_filter_queries (List[dict]): List of filter queries to identify items.

        Returns:
            DeleteResult: The result of the delete operation.
        """
        return await self.repository.delete_many(key_filter_queries)
