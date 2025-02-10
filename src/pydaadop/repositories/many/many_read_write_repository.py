"""
This module provides the ManyReadWriteRepository class, which implements the repository
for reading and writing multiple MongoDB models.

Classes:
    ManyReadWriteRepository: A repository class for reading and writing multiple MongoDB models.
"""

from typing import Type, TypeVar, Generic, List, Optional, Dict

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne
from pymongo.results import InsertManyResult, DeleteResult, BulkWriteResult

from ..base.base_read_write_repository import BaseReadWriteRepository
from ...models.base import BaseMongoModel

T = TypeVar("T", bound=BaseMongoModel)

class ManyReadWriteRepository(BaseReadWriteRepository[T]):
    """
    A repository class for reading and writing multiple MongoDB models.

    Attributes:
        collection (AsyncIOMotorCollection): The MongoDB collection.
    """

    def __init__(self, model: Type[T], collection: AsyncIOMotorCollection = None):
        """
        Initialize the ManyReadWriteRepository.

        Args:
            model (Type[T]): The MongoDB model type.
            collection (AsyncIOMotorCollection, optional): The MongoDB collection. Defaults to None.
        """
        super().__init__(model, collection)

    async def create_many(self, items: List[T]) -> InsertManyResult:
        """
        Create multiple items.

        Args:
            items (List[T]): The list of items to create.

        Returns:
            InsertManyResult: The result of the insert operation.
        """
        serialized_items = [item.model_dump(by_alias=True) for item in items]
        return await self.collection.insert_many(serialized_items, ordered=False)

    async def update_many(self, items: List[T]) -> BulkWriteResult:
        """
        Update multiple items.

        Args:
            items (List[T]): The list of items to update.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        bulk_write_operations = [UpdateOne(item.model_dump_keys(), {"$set": item.model_dump()}) for item in items]
        return await self.collection.bulk_write(bulk_write_operations)

    async def update_field_many(self, keys_filter_query: List[dict], data: dict) -> BulkWriteResult:
        """
        Update a field of multiple items.

        Args:
            keys_filter_query (List[dict]): The list of key filter queries.
            data (dict): The data to update.

        Returns:
            BulkWriteResult: The result of the update operation.
        """
        bulk_write_operations = [UpdateOne(key_filter, {"$set": data}) for key_filter in keys_filter_query]
        return await self.collection.bulk_write(bulk_write_operations)

    async def delete_many(self, keys_filter_query: List[dict]) -> DeleteResult:
        """
        Delete multiple items.

        Args:
            keys_filter_query (List[dict]): The list of key filter queries.

        Returns:
            DeleteResult: The result of the delete operation.
        """
        return await self.collection.delete_many({"$or": keys_filter_query})
