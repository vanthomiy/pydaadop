"""
This module provides the ManyReadWriteServiceInterface class, which defines the interface
for reading and writing multiple MongoDB models.

Classes:
    ManyReadWriteServiceInterface: An interface for reading and writing multiple MongoDB models.
"""

from abc import abstractmethod
from typing import TypeVar, Type, List
from pydantic import BaseModel
from pymongo import UpdateMany
from pymongo.results import InsertManyResult, BulkWriteResult

from .read_service_interface import ReadServiceInterface
from .read_write_service_interface import ReadWriteServiceInterface
from ...models.base import BaseMongoModel
from ...repositories.base.base_repository import BaseRepository

S = TypeVar('S', bound=BaseMongoModel)

@abstractmethod
class ManyReadWriteServiceInterface(ReadWriteServiceInterface[S]):
    """
    An interface for reading and writing multiple MongoDB models.
    """

    @abstractmethod
    async def create_many(self, item: [S]) -> InsertManyResult:
        """
        Create multiple items.

        Args:
            item (List[S]): The list of items to create.

        Returns:
            InsertManyResult: The result of the insert operation.
        """
        pass

    @abstractmethod
    async def update_many(self, items: [S]) -> BulkWriteResult:
        """
        Update multiple items.

        Args:
            items (List[S]): The list of items to update.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        pass

    @abstractmethod
    async def update_field_many(self, key_filter_queries: List[dict], data: dict) -> BulkWriteResult:
        """
        Update a field of multiple items.

        Args:
            key_filter_queries (List[dict]): The list of key filter queries.
            data (dict): The data to update.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        pass

    @abstractmethod
    async def delete_many(self, key_filter_queries: [dict]) -> None:
        """
        Delete multiple items.

        Args:
            key_filter_queries (List[dict]): The list of key filter queries.
        """
        pass

